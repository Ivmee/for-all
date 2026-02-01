#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import threading
from time import sleep, time
import wx
import wx.lib.plot as wxPlot
import wx.lib.newevent
from MagicMeasure_GUI import MainFrameGUI
import os, sys
from random import random
from queue import Queue
from copy import copy
import subprocess
import signal
import serial.tools.list_ports
import re

DRYRUN = False

timing = 0.025


def get_available_ports():
    """Возвращает отсортированный список портов (сначала USB/Virtual, потом остальные)."""
    try:
        ports_objects = serial.tools.list_ports.comports()
        port_names = [p.device for p in ports_objects]
    except:
        return ["/dev/ttyS0", "COM1"]

    # Функция для натуральной сортировки (разбивает 'COM10' на ['COM', 10])
    def natural_key(string_):
        return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', string_)]

    # Приоритет: USB и ACM выше, чем ttyS
    def priority_key(string_):
        if 'USB' in string_ or 'ACM' in string_ or 'COM' in string_:
            return 0 
        return 1

    port_names.sort(key=lambda s: (priority_key(s), natural_key(s)))
    return port_names



try:
	from pymeasure.instruments.keithley import Keithley2400
	from pymeasure.adapters import SerialAdapter
except:
	DRYRUN = True



class Command:
	def __init__(self, name, args):
		self.name = copy(name)
		self.args = copy(args)
		

class CommandServerClass:
	def __init__(self,gui_class):
		self.CommandQueue = Queue()
		self.STOP = False
		self.BUSY = False
				
		self.gui = gui_class
		
		if not DRYRUN:
			self.HardwareInit()
	
	def HardwareInit(self, meas_port=None,comm_port=None):
		def send_status(message, color, target='MEAS'):
			if hasattr(self, 'gui'):
				self.gui.CallbackData.Lock()
				# Передаем target в событие
				event = self.gui.CallbackEventGeneral(command='STATUS', msg=message, color=color, target=target)
				wx.QueueEvent(self.gui.GetEventHandler(), event)
				self.gui.CallbackData.Unlock()

		# 1. Сначала закрываем старое соединение, если оно уже есть
		if meas_port or (meas_port is None and comm_port is None):
			if hasattr(self, 'MeasAdapter') and self.MeasAdapter:
				try:
					self.MeasAdapter.connection.close()
				except:
					pass

			# 2.  выбор пути к порту
			if meas_port:
				# Если порт передан аргументом (из GUI), используем его
				MeasAdapterPath = meas_port
				# Сбрасываем хендлер эмулятора, так как мы на реальном железе
				self.MeasAdapterHandler = None 
			else:
				# ЕСЛИ ПОРТ НЕ ВЫБРАН
				MeasAdapterPath = "/dev/ttyS0"
				self.MeasAdapterHandler = None
				if not os.path.exists(MeasAdapterPath):
					print("meas emulation mode") # Эмуляция
					MeasAdapterPath = "/home/user/Temp/ttyV0"
					# Проверяем, запущен ли уже socat, если нет - запускаем
					if not os.path.exists(MeasAdapterPath):
						self.MeasAdapterHandler = subprocess.Popen(["socat", "-d", "-d", "pty,raw,echo=0,link=/home/user/Temp/ttyV0", "pty,raw,echo=0,link=/home/user/Temp/ttyV1"])
						sleep(0.5)

			print(f"Connecting to MeasAdapter at: {MeasAdapterPath}")
			send_status("Connecting", wx.Colour(200, 150, 0),target='MEAS')
			# Сохраняем выбранный путь в переменную класса, чтобы потом сравнить
			self.MeasAdapterPath = MeasAdapterPath
			# 3. Подключение к прибору 
			try:
				self.MeasAdapter = SerialAdapter(MeasAdapterPath,
										baudrate=57600,
										timeout=0.1,
										write_timeout=0.1)
				
				self.SoureMeter = Keithley2400(self.MeasAdapter)
				self.SoureMeter.reset()
				self.SoureMeter.use_front_terminals()
				
				# Восстанавливаем настройки (Front/Rear) из положения слайдера в GUI
				# Проверяем, существует ли gui, на случай сухого запуска
				if hasattr(self, 'gui') and self.gui.InputSlider.GetValue():
					self.SoureMeter.use_rear_terminals()
					
				print("Keithley Connected Successfully!")
				send_status("Connected", wx.Colour(0, 180, 0),target='MEAS')

			except Exception as e:
				print(f"Connection Error: {e}")
				err_msg = str(e).split('(')[0][:25]
				send_status("Error", wx.Colour(255, 0, 0),target='MEAS')


		
		# КОММУТАТОР (
		# Выполняем, если передан comm_port ИЛИ если это первый запуск (оба None)
		if comm_port or (meas_port is None and comm_port is None):
			# 1. Закрываем старое
			if hasattr(self, 'CommutatorAdapter') and self.CommutatorAdapter:
				try: self.CommutatorAdapter.connection.close()
				except: pass
			
			# 2. Выбираем путь
			if comm_port:
				CommPath = comm_port
				self.CommutatorAdapterHandler = None
			else:
				
				CommPath = "/dev/ttyACM0"
				self.CommutatorAdapterHandler = None
				if not os.path.exists(CommPath):
					
					CommPath = "/home/user/Temp/ttyV2"
					if not os.path.exists(CommPath):
						self.CommutatorAdapterHandler = subprocess.Popen(["socat", "-d", "-d", "pty,raw,echo=0,link=/home/user/Temp/ttyV2", "pty,raw,echo=0,link=/home/user/Temp/ttyV3"])
						sleep(0.5)
				# ПРОВЕРКА НА ДУБЛИРОВАНИЕ ПОРТОВ
			# Получаем текущий порт Keithley
			current_keithley = getattr(self, 'MeasAdapterPath', None)
			
			if current_keithley and CommPath == current_keithley:
				print(f"CONFLICT: Port {CommPath} is busy by Keithley!")
				send_status("Port Conflict!", wx.Colour(255, 0, 0), target='COMM')
				# Прерываем выполнение
				return
			print(f"Connecting Commutator to: {CommPath}")
			send_status("Connecting...", wx.Colour(200, 150, 0), target='COMM')

			# 3. Подключение
			try:
				self.CommutatorAdapter = SerialAdapter(CommPath, baudrate=9600, timeout=0.1, write_timeout=0.1)
				print("Commutator Connected!")
				send_status("Connected", wx.Colour(0, 180, 0), target='COMM')
			except Exception as e:
				print(f"Commutator Error: {e}")
				err_msg = str(e).split('(')[0][:20]
				send_status("Error: ", wx.Colour(255, 0, 0), target='COMM')
		
	
	def runCHANNEL(self, command):
		args = command.args
		commands = ['','LD','RD','LU','RU','OFF']
		modificators = ['','+','-','4+','4-']
		command = commands[args[0]] + modificators[args[1]]
		if not DRYRUN:
			self.CommutatorAdapter.write(command)
	
	def runINPUT(self, command):
		if DRYRUN: return
		if command.args[0]:	self.SoureMeter.use_rear_terminals()
		else:				self.SoureMeter.use_front_terminals()
	
	def runIVcycle(self, command):
		print(command.name, command.args)
		command_down = Command(command.name, command.args)
		command_down.args[0] = command.args[1]
		command_down.args[1] = command.args[0]
		command_down.args[2] = -command.args[2]
		
		
		if command.args[5]:
			if not DRYRUN:
				self.SoureMeter.apply_voltage(compliance_current=command.args[3])
				self.SoureMeter.measure_current()
				self.SoureMeter.enable_source()
				
			for cycle in range(command.args[4]):
				self.runIV(command)
				if self.STOP: break
				self.runIV(command_down)
				if self.STOP: break
			
			if not DRYRUN:
				self.SoureMeter.disable_source()
				self.SoureMeter.shutdown()
			return
		
		for cycle in range(command.args[4]):
				self.runIV(command)
				if self.STOP: return
				
	# ~ def runIVcycle(self, command):
		# ~ self.runIV(command)
	
	def runIV(self, command):
		
		self.gui.CallbackData.Lock()
		event = self.gui.CallbackEventGeneral(command = 'setupIV')
		wx.QueueEvent(self.gui.GetEventHandler(), event)
		self.gui.CallbackData.LockUnlock()
		SavePath = copy(self.gui.CallbackData.var_str)
		
		args = command.args
		minV = args[0]
		maxV = args[1]
		dV = args[2]
		# ~ if minV>maxV: dV *= -1.
		Voltages = np.arange(minV,maxV*1.00001,dV)
		if not len(Voltages): Voltages = np.arange(minV,maxV*1.00001,-dV)
		currLim = args[3]
		
		
		# ~ if DRYRUN:
			# ~ self.CommandBuffer['busy']=0
			# ~ continue
		
		if (not DRYRUN) and (not args[5]):
			self.SoureMeter.apply_voltage(compliance_current=currLim)
			self.SoureMeter.measure_current()
			self.SoureMeter.enable_source()
		
		out = open(SavePath,'w')
		for iv,voltage in enumerate(Voltages):
			if self.STOP:
				self.CommandQueue.queue.clear()
				break
			
			# GET current
			if not DRYRUN:
				self.SoureMeter.source_voltage = voltage
				sleep(timing)
				self.MeasAdapter.write(':read?')
				sleep(timing)
				#curr = random()
				textcurr = self.MeasAdapter.read().replace('E','e').replace('\r','').replace('\n','')
				print(voltage, textcurr)
				try:
					curr = float(textcurr)
				except:
					curr = 0.0
				#sleep(0.1)
			else:
				curr = random()
				sleep(0.05)
			
			point = (voltage, curr)

			
			event = self.gui.CallbackEventCurrent(data = np.array([point]))
			wx.QueueEvent(self.gui.GetEventHandler(), event)
			
			# Сохранение текущего измерения
			out.write('%.6e\t%.6e\n' % point)
			
			
		
		if (not DRYRUN) and (not args[5]):
			self.SoureMeter.disable_source()
			self.SoureMeter.shutdown()
		
		
		# Закрываем файл
		out.close()
		
		# Завершаем процедуру
		self.gui.CallbackData.Lock()
		event = self.gui.CallbackEventGeneral(command = 'endIV')
		wx.QueueEvent(self.gui.GetEventHandler(), event)
		self.gui.CallbackData.LockUnlock()
		
		
		


	def runIT(self, command):
		self.gui.CallbackData.Lock()
		event = self.gui.CallbackEventGeneral(command = 'setupIT')
		wx.QueueEvent(self.gui.GetEventHandler(), event)
		self.gui.CallbackData.LockUnlock()
		SavePath = copy(self.gui.CallbackData.var_str)
		
		dT      = command.args[0]
		endT    = command.args[1]
		Voltage = command.args[2]
		currLim = command.args[3]

		# ~ if DRYRUN:
			# ~ self.CommandBuffer['busy']=0
			# ~ continue
		
		if not DRYRUN:
			self.SoureMeter.apply_voltage(compliance_current=currLim)
			self.SoureMeter.measure_current()
			self.SoureMeter.enable_source()
			sleep(timing)
			self.SoureMeter.source_voltage = Voltage
			sleep(timing)
		
		out = open(SavePath,'w')
		startindex_disp = 0
		isDispFull = False
		dT_disp = 300			# Отображаемый интервал точек
		StartTime = time()
		prevtime = time()-StartTime
		while prevtime<endT:
			if self.STOP:
				self.CommandQueue.queue.clear()
				break
			
			# GET current
			currtime = time()-StartTime
			if not DRYRUN:
				self.MeasAdapter.write(':read?')
				sleep(timing)
				#curr = random()
				textcurr = self.MeasAdapter.read().replace('E','e').replace('\r','').replace('\n','')
				print(currtime, textcurr)
				try:
					curr = float(textcurr)
				except:
					curr = 0.0
				#sleep(0.1)
			else:
				curr = random()
				sleep(0.1)
				
			point = (currtime, curr)

			isDispFull = (currtime>dT_disp)
			if currtime>dT_disp: startindex_disp+=1

			self.gui.CallbackData.Lock()
			event = self.gui.CallbackEventCurrent(	data = np.array([point]),
													isDispFull = isDispFull)
			wx.QueueEvent(self.gui.GetEventHandler(), event)
			
			# Сохранение текущего измерения
			out.write('%.6e\t%.6e\n' % point)
			
			# Проверить, есть ли остаток времени на сон
			currtime = time()-StartTime
			restTime = dT - (currtime-prevtime)
			prevtime = currtime
			if restTime>0: sleep(restTime)
		
		if not DRYRUN:
			self.SoureMeter.disable_source()
			self.SoureMeter.shutdown()
		
		# Закрываем файл
		out.close()
		
		# Завершаем процедуру
		self.gui.CallbackData.Lock()
		event = self.gui.CallbackEventGeneral(command = 'endIT')
		wx.QueueEvent(self.gui.GetEventHandler(), event)
		self.gui.CallbackData.LockUnlock()
		


	def runMEM(self, command):
		self.gui.CallbackData.Lock()
		event = self.gui.CallbackEventGeneral(command = 'setupMEM')
		wx.QueueEvent(self.gui.GetEventHandler(), event)
		self.gui.CallbackData.LockUnlock()
		SavePath = copy(self.gui.CallbackData.var_str)
		
		SetV		= command.args[0]	# 0
		SetT		= command.args[1]	# 1
		SetP		= command.args[2]	# 2
		ClearV		= command.args[3]	# 3
		ClearT		= command.args[4]	# 4
		ClearP		= command.args[5]	# 5
		ReadV		= command.args[6]	# 6
		ReadT		= command.args[7]	# 7
		ReadP		= command.args[8]	# 8
		ReadCycles	= command.args[9]	# 9
		TotCycles	= command.args[10]	# 10
		currLim		= command.args[11]	# 11
		
		WaitV       = 0.0	# Напряжение в режиме ожидания
		
		# ~ if DRYRUN:
			# ~ self.CommandBuffer['busy']=0
			# ~ continue
		
		if not DRYRUN:
			try:
				self.SoureMeter.apply_voltage(compliance_current=currLim)
				self.SoureMeter.measure_current()
				self.SoureMeter.enable_source()
				sleep(timing)
				self.SoureMeter.source_voltage = WaitV
				sleep(timing)
			except Exception as e:
				print(f'error {e}')
				return
		
		out = open(SavePath,'w')
		startindex_disp = 0
		isDispFull = False
		dT_disp = 300			# Отображаемый интервал точек
		
		readCycleTime = (ReadT+ReadP)*ReadCycles
		totCycleTime  = (SetT+SetP) + readCycleTime + (ClearT+ClearP) + readCycleTime
		
		
		def vlotageFromTime(t):
			dt = round(t % totCycleTime, 3)
			if dt<(SetT+SetP):
				if dt<SetT: return (SetV, 0)
				return (WaitV, 1)
			
			dt -= (SetT+SetP)
			if dt<readCycleTime:
				dt = round(dt % (ReadT+ReadP), 3)
				if dt<ReadT: return (ReadV, 2)
				return (WaitV, 3)
			
			dt -= readCycleTime
			if dt<(ClearT+ClearP):
				if dt<ClearT: return (ClearV, 4)
				return (WaitV, 5)
			
			dt -= (ClearT+ClearP)
			dt = round(dt % (ReadT+ReadP), 3)
			if dt<ReadT: return (ReadV, 6)
			return (WaitV, 7)
		
		StartTime = time()
		currtime = time()-StartTime
		preV = WaitV
		
		while True:
			if self.STOP:
				self.CommandQueue.queue.clear()
				break
			
			# Измерение тока
			currtime = time()-StartTime
			totCycle = int(currtime/totCycleTime)
			if totCycle >= TotCycles: break
			currV, cycleState = vlotageFromTime(currtime)
			if currV!=preV:
				if not DRYRUN: self.SoureMeter.source_voltage = currV
				sleep(timing)
			
			preV = currV
			
			if not DRYRUN:
				self.MeasAdapter.write(':read?')
				sleep(timing)
				#curr = random()
				textcurr = self.MeasAdapter.read().replace('E','e').replace('\r','').replace('\n','')
				print(currtime, textcurr)
				try:
					curr = float(textcurr)
				except:
					curr = 0.0
				#sleep(0.1)
			else:
				curr = currV
				sleep(0.1)
			
			
			point = (currtime, curr)

			isDispFull = (currtime>dT_disp)
			if currtime>dT_disp: startindex_disp+=1

			self.gui.CallbackData.Lock()
			event = self.gui.CallbackEventCurrent(	data = np.array([point]),
													isDispFull = isDispFull)
			wx.QueueEvent(self.gui.GetEventHandler(), event)
			
			# Сохранение текущего измерения
			out.write('%.6e\t%.6e\t%d\t%d\n' % (currtime, curr, totCycle, cycleState))
			
		
		if not DRYRUN:
			self.SoureMeter.disable_source()
			self.SoureMeter.shutdown()
		
		# Закрываем файл
		out.close()
		
		# Завершаем процедуру
		self.gui.CallbackData.Lock()
		event = self.gui.CallbackEventGeneral(command = 'endMEM')
		wx.QueueEvent(self.gui.GetEventHandler(), event)
		self.gui.CallbackData.LockUnlock()

	
	
	def run(self):
		print('Command Server Started')
		while 1:
			command = self.CommandQueue.get()
			print(command.name, command.args)
			
			if   command.name == 'EXIT':
				# ~ print("exit")
				if self.MeasAdapterHandler:		self.MeasAdapterHandler.send_signal(signal.SIGTERM)
				if self.CommutatorAdapterHandler:	self.CommutatorAdapterHandler.send_signal(signal.SIGTERM)
				break
			elif command.name == 'SET_PORT':
				# Аргумент 0 - это имя порта, которое прислал GUI
				new_port = command.args[0]
				print(f"Server: Switching port to {new_port}")
				self.HardwareInit(meas_port=new_port)
			elif command.name == 'SET_COMM_PORT':
				new_comm_port = command.args[0]
				print(f"Server: Switching COMMUTATOR to {new_comm_port}")
				self.HardwareInit(comm_port=new_comm_port)
			elif command.name == 'CHANNEL':	self.runCHANNEL(command)
			elif command.name == 'INPUT':	self.runINPUT(command)
			# ~ elif command.name == 'IV':		self.runIV(command)
			elif command.name == 'IV':		self.runIVcycle(command)
			elif command.name == 'IT':		self.runIT(command)
			elif command.name == 'MEM':		self.runMEM(command)
			elif command.name == 'EMPTY':	pass
			
			if self.STOP: self.STOP = False
	

class CallbackClass:
	def __init__(self):
		self.lock     = threading.Lock()
		self.var_bool = False
		self.var_int  = 0
		self.var_list = None
		self.var_dict = None
		self.var_str  = None
		self.var_str2 = None
		self.var_obj  = None
		self.var_exec = None
		
	def Lock(self):
		self.lock.acquire()
		
	def Unlock(self):
		self.lock.release()
		
	def LockUnlock(self):
		self.lock.acquire()
		self.lock.release()
		


class CurvesItem:
	def __init__(self, curve, mode=0):
		# ~ self.data = np.array(data)
		self.curve = curve
		self.mode  = mode

class MainFrame(MainFrameGUI):
	def __init__(self, parent, **kwargs):
		super().__init__(parent, **kwargs)
		
		self.SettingsPanelWidth = 300
		self._resize()
		
		self.lastFilenames = ['IV_meas','IT_meas','MEM_meas']
		self.FileName.Value = self.lastFilenames[self.ModeNB.Selection]
		
		self.DataTables = {}
		self.Colors = [	wx.Colour(0,0,0),
						wx.Colour(255,0,0),
						wx.Colour(0,0,255),
						wx.Colour(254,166,1),
						wx.Colour(155,206,61),
						wx.Colour(71,131,181),
						wx.Colour(223,83,107),
						wx.Colour(97,208,79),
						wx.Colour(34,151,230),
						wx.Colour(40,226,229),
						wx.Colour(205,11,188),
						wx.Colour(245,199,16),
						wx.Colour(158,158,158),
						wx.Colour(34,139,34),
						wx.Colour(178,34,34),
						wx.Colour(255,215,0),
						wx.Colour(70,130,180),
						wx.Colour(102,0,0),
						wx.Colour(230,107,0),
						]
		
		self.CallbackData = CallbackClass()
		self.CallbackEventGeneral, self.EVT_CALLBACK_EVENT_GENERAL = wx.lib.newevent.NewEvent()
		self.CallbackEventCurrent, self.EVT_CALLBACK_EVENT_CURRENT = wx.lib.newevent.NewEvent()
		self.Bind(self.EVT_CALLBACK_EVENT_GENERAL, self.CSCallbackGeneral)

		
		self.CommandServer = CommandServerClass(self)
		self.CommandServerThread = threading.Thread(target=self.CommandServer.run)
		self.CommandServerThread.start()

		# Регистрация события для обратной передачи данных в GUI из коммандного сервера
		# self.CallbackEvent будет использоваться для создания экземпляра события в коммандном сервере
		

		self.GraphRedraw()
		self.Maximize(True)
		
		# Выключение релюх коммутатора
		self.CommandServer.CommandQueue.put(Command('CHANNEL', [5, 0, True]))
		self.onScanPorts(None)
	

	def onScanPorts(self, event):
		"""Нажатие кнопки Scan"""
		ports = get_available_ports()
		
		# PortSelector - это имя переменной из wxFormBuilder
		self.PortSelector.Clear()
		self.PortSelector.SetItems(ports)
		
		if ports:
			self.PortSelector.SetSelection(0)
		else:
			self.PortSelector.Append("No ports found")
			self.PortSelector.SetSelection(0)

			#Коммутатор
		if hasattr(self, 'CommPortSelector'):
			self.CommPortSelector.Clear()
			self.CommPortSelector.SetItems(ports)
			if ports: 
				# Попробуем выбрать второй порт по умолчанию, если он есть
				idx = 1 if len(ports) > 1 else 0
				self.CommPortSelector.SetSelection(idx)
			else: 
				self.CommPortSelector.Append("No ports")

	def onPortSelected(self, event):
		"""Выбор из выпадающего списка"""
		selected_port = self.PortSelector.GetValue()
		
		#  защита от пустых значений
		if selected_port and "No ports" not in selected_port:
			print(f"GUI: Sending request to set port: {selected_port}")
			# Отправляем команду серверу
			self.CommandServer.CommandQueue.put(Command('SET_PORT', [selected_port]))
	def onCommPortSelected(self, event):
		"""Выбор порта для Коммутатора"""
		selected = self.CommPortSelector.GetValue()
		if selected and "No ports" not in selected:
			print(f"GUI: Set Commutator -> {selected}")
			self.CommandServer.CommandQueue.put(Command('SET_COMM_PORT', [selected]))	


	def _resize(self):
		allsize = self.Size
		self.SettingsPanel.SetSize(self.SettingsPanelWidth,allsize[1])
		self.m_notebook1.SetSize(self.Size[0]-self.SettingsPanelWidth-20,allsize[1]-50)
		# ~ self.GraphPanel.SetSize(self.Size[0]-self.SettingsPanelWidth,-1)
		self.SettingsPanel.SetPosition((self.Size[0]-self.SettingsPanelWidth-10,0))
		
		# ~ sizeX = int(self.GraphPanel.Size[0])
		# ~ sizeY = int(self.GraphPanel.Size[1])
		
		# ~ self.MainDraw.SetSize(int(sizeX*0.7), int(sizeY*0.7))
		# ~ self.MainDraw.SetPosition((0, 0))
		# ~ self.AllDraw.SetSize(int(sizeX*0.3), int(sizeY*0.3))
		# ~ self.AllDraw.SetPosition((int(sizeX*0.7), 0))
		
		
		return
	
	def _resize2(self):
		windowSize = self.Size
		print(windowSize)
		self.SettingsPanel.SetSize(self.SettingsPanelWidth, self.Size[1])
		self.m_notebook1.SetSize(self.Size[0]-self.SettingsPanelWidth-20, self.Size[1]-50)
		# ~ self.GraphPanel.SetSize(self.Size[0]-self.SettingsPanelWidth,-1)
		self.SettingsPanel.SetPosition((self.Size[0]-self.SettingsPanelWidth-10, -1))

		# Изменение размера области прокрутки
		# ~ vsize = windowSize[1]-(self.NamesPanel.Position[1]+self.NamesPanel.Size[1])-3
		# ~ self.AllCurvesList.Size = (-1, vsize)
		
		
		# ~ print('Plot size:', self.m_notebook1.Size)
		# ~ print('Sett size:', self.SettingsPanel.Size)
		# ~ print('Bot size:', self.NamesPanel.Size)
		# ~ print('Bot pos:', self.NamesPanel.Position)
		# ~ print('Curv size:', self.AllCurvesList.Size)
		# ~ print('Vsize size:', vsize)
		
		
		
		
		# ~ sizeX = int(self.GraphPanel.Size[0])
		# ~ sizeY = int(self.GraphPanel.Size[1])
		
		# ~ self.MainDraw.SetSize(int(sizeX*0.7), int(sizeY*0.7))
		# ~ self.MainDraw.SetPosition((0, 0))
		# ~ self.AllDraw.SetSize(int(sizeX*0.3), int(sizeY*0.3))
		# ~ self.AllDraw.SetPosition((int(sizeX*0.7), 0))
		return
	
	
	def onSize(self,event):
		self._resize()
		return
		
	
	def CSCallbackGeneral(self, event):


		command = event.command
		if command == 'STATUS':
			# Получаем цель сообщения  Keithley)\
			target = getattr(event, 'target', 'MEAS')
			
			msg = event.msg
			color = event.color
			
			if target == 'MEAS':
				# Обновляем  статус (Keithley)
				if hasattr(self, 'StatusLabel'):
					self.StatusLabel.SetLabel(msg)
					self.StatusLabel.SetForegroundColour(color)
			
			elif target == 'COMM':
				# Обновляем  статус (Коммутатор)
				if hasattr(self, 'StatusLabel1'):
					self.StatusLabel1.SetLabel(msg)
					self.StatusLabel1.SetForegroundColour(color)
			
			self.SettingsPanel.Layout() # Обновляем верстку
			return	


		if command == 'setupIT':
			dirname  = self.SaveDir.GetLineText(0)
			filename = self.FileName.GetLineText(0).split('.txt')[0]
			if self.InctementModifier.Value: filename += '_%04d' % int(self.IncrementSuffix.Value)
			filename += '.txt'
			self.CallbackData.var_str  = os.path.join(dirname, filename)
			self.CallbackData.var_str2 = filename
			
			self.GraphRedraw(filename)
			
			# Установка переменных выолнения
			is_repeat = int(filename in list(self.DataTables.keys()))
			self.CallbackData.var_bool = bool(is_repeat)
			self.CallbackData.var_obj  = self.Colors[(self.AllCurvesList.Count - is_repeat)  % len(self.Colors)]	
			self.Bind(self.EVT_CALLBACK_EVENT_CURRENT, self.CSCallbackIT)
			
			# MainLines filter
			self.MainLines = [line for line in self.MainLines if (len(line._points)!=1 or (line._points[0,0] or line._points[0,0]))]
			# End filter
		
		elif command == 'endIT':
			self.Unbind(self.EVT_CALLBACK_EVENT_CURRENT)
			data = np.genfromtxt(self.CallbackData.var_str)[:,:2]
			self.DataTables[self.CallbackData.var_str2].curve = wxPlot.PolyLine(data, colour=self.CallbackData.var_obj, width=3)
			if self.InctementModifier.Value: self.IncrementSuffix.Value += 1
			
			self.GraphRedraw()
			
		elif command == 'setupIV':
			dirname  = self.SaveDir.GetLineText(0)
			filename = self.FileName.GetLineText(0).split('.txt')[0]
			if self.InctementModifier.Value: filename += '_%04d' % int(self.IncrementSuffix.Value)
			filename += '.txt'
			self.CallbackData.var_str  = os.path.join(dirname, filename)
			self.CallbackData.var_str2 = filename
			
			self.GraphRedraw(filename)
			
			# Установка переменных выолнения
			is_repeat = int(filename in list(self.DataTables.keys()))
			self.CallbackData.var_bool = bool(is_repeat)
			self.CallbackData.var_obj  = self.Colors[(self.AllCurvesList.Count - is_repeat)  % len(self.Colors)]	
			# ~ self.CallbackData.var_exec = self.CSCallbackIT
			self.Bind(self.EVT_CALLBACK_EVENT_CURRENT, self.CSCallbackIV)

			# MainLines filter
			self.MainLines = [line for line in self.MainLines if (len(line._points)!=1 or (line._points[0,0] or line._points[0,0]))]
			# End filter

		elif command == 'endIV':
			self.Unbind(self.EVT_CALLBACK_EVENT_CURRENT)
			data = np.genfromtxt(self.CallbackData.var_str)[:,:2]
			self.DataTables[self.CallbackData.var_str2].curve = wxPlot.PolyLine(data, colour=self.CallbackData.var_obj, width=3)
			if self.InctementModifier.Value: self.IncrementSuffix.Value += 1
			
			self.GraphRedraw()
			
		elif command == 'setupMEM':
			dirname  = self.SaveDir.GetLineText(0)
			filename = self.FileName.GetLineText(0).split('.txt')[0]
			if self.InctementModifier.Value: filename += '_%04d' % int(self.IncrementSuffix.Value)
			filename += '.txt'
			self.CallbackData.var_str  = os.path.join(dirname, filename)
			self.CallbackData.var_str2 = filename
			
			self.GraphRedraw(filename)
			
			# Установка переменных выолнения
			is_repeat = int(filename in list(self.DataTables.keys()))
			self.CallbackData.var_bool = bool(is_repeat)
			self.CallbackData.var_obj  = self.Colors[(self.AllCurvesList.Count - is_repeat)  % len(self.Colors)]	
			self.Bind(self.EVT_CALLBACK_EVENT_CURRENT, self.CSCallbackMEM)
			
			# MainLines filter
			self.MainLines = [line for line in self.MainLines if (len(line._points)!=1 or (line._points[0,0] or line._points[0,0]))]
			# End filter
		
		elif command == 'endMEM':
			self.Unbind(self.EVT_CALLBACK_EVENT_CURRENT)
			data = np.genfromtxt(self.CallbackData.var_str)[:,:2]
			self.DataTables[self.CallbackData.var_str2].curve = wxPlot.PolyLine(data, colour=self.CallbackData.var_obj, width=3)
			if self.InctementModifier.Value: self.IncrementSuffix.Value += 1
			
			self.GraphRedraw()
			
			
			
		self.CallbackData.Unlock()
						
			
	def CSCallbackIV(self, event):
		point          = event.data
		current_colour = self.CallbackData.var_obj
		filename       = self.CallbackData.var_str2

		# Проверка. Была ли уже такая кривая.
		if not self.CallbackData.var_bool:
			current_line = wxPlot.PolyLine(point, colour=current_colour, width=3)
			self.DataTables[filename] = CurvesItem(current_line, mode=0)
			self.AllCurvesList.Insert(filename,0)
			self.AllCurvesList.Check(0)
			self.CallbackData.var_bool = True
		else:
			data = np.concatenate((self.DataTables[filename].curve._points, point), axis=0)
			current_line = wxPlot.PolyLine(data, colour=current_colour, width=3)
			self.DataTables[filename].curve = current_line
		
		# ~ self.MainGraph = wxPlot.PlotGraphics([current_line] + self.MainLines,'','Time, s','Current, A')
		self.MainGraph = wxPlot.PlotGraphics([current_line] + self.MainLines,'','Voltage, V','Current, A')
		self.MainDraw.Draw(self.MainGraph)
		self.SettingsPanel.SetFocus()
		self.MainDraw.SetFocus()

		
		
			
	def CSCallbackIT(self, event):
		point          = event.data
		isDispFull     = event.isDispFull
		current_colour = self.CallbackData.var_obj
		filename       = self.CallbackData.var_str2
				
		# Проверка. Была ли уже такая кривая.
		if not self.CallbackData.var_bool:
			current_line = wxPlot.PolyLine(point, colour=current_colour, width=3)
			self.DataTables[filename] = CurvesItem(current_line, mode=1)
			self.AllCurvesList.Insert(filename,0)
			self.AllCurvesList.Check(0)
			self.CallbackData.var_bool = True
		else:
			if isDispFull:	# Если область отображения уже заполнена, то нечего выделять память.
				data = np.roll(self.DataTables[filename].curve._points, -2)
				data[-1] = np.copy(point[0])
			else:			# Если нет, то расширим массив
				data = np.concatenate((self.DataTables[filename].curve._points, point), axis=0)
			# ~ self.DataTables[filename].curve._points = data
			# ~ current_line = self.DataTables[filename].curve
			current_line = wxPlot.PolyLine(data, colour=current_colour, width=3)
			self.DataTables[filename].curve = current_line
		
		# ~ self.MainGraph = wxPlot.PlotGraphics([current_line] + self.MainLines,'','Time, s','Current, A')
		self.MainGraph = wxPlot.PlotGraphics([current_line],'','Time, s','Current, A')
		self.MainDraw.Draw(self.MainGraph)
		self.SettingsPanel.SetFocus()
		self.MainDraw.SetFocus()

		self.CallbackData.Unlock()
	
	def CSCallbackMEM(self, event):
		point          = event.data
		isDispFull     = event.isDispFull
		current_colour = self.CallbackData.var_obj
		filename       = self.CallbackData.var_str2
				
		# Проверка. Была ли уже такая кривая.
		if not self.CallbackData.var_bool:
			current_line = wxPlot.PolyLine(point, colour=current_colour, width=3)
			self.DataTables[filename] = CurvesItem(current_line, mode=2)
			self.AllCurvesList.Insert(filename,0)
			self.AllCurvesList.Check(0)
			self.CallbackData.var_bool = True
		else:
			if isDispFull:	# Если область отображения уже заполнена, то нечего выделять память.
				data = np.roll(self.DataTables[filename].curve._points, -2)
				data[-1] = np.copy(point[0])
			else:			# Если нет, то расширим массив
				data = np.concatenate((self.DataTables[filename].curve._points, point), axis=0)
			# ~ self.DataTables[filename].curve._points = data
			# ~ current_line = self.DataTables[filename].curve
			current_line = wxPlot.PolyLine(data, colour=current_colour, width=3)
			self.DataTables[filename].curve = current_line
		
		# ~ self.MainGraph = wxPlot.PlotGraphics([current_line] + self.MainLines,'','Time, s','Current, A')
		self.MainGraph = wxPlot.PlotGraphics([current_line],'','Time, s','Current, A')
		self.MainDraw.Draw(self.MainGraph)
		self.SettingsPanel.SetFocus()
		self.MainDraw.SetFocus()

		self.CallbackData.Unlock()
	
	def GraphRedraw(self, current_filename=''):
		mode = self.ModeNB.Selection	# IV or IT
		xlabel 			= 'Voltage, V'
		if mode: xlabel	= 'Time, s'
		
		if self.CurveModifier.Value: [self.AllCurvesList.Check(index, False) for index in range(self.AllCurvesList.Count)]
		self.MainDraw.Reset()
		self.MainLines = [self.DataTables[filename].curve for filename in self.AllCurvesList.GetCheckedStrings() if (filename!=current_filename and self.DataTables[filename].mode==mode)]
		if not self.MainLines: self.MainLines = [wxPlot.PolyLine([(0,0)], colour='black', width=1)]
		self.MainGraph = wxPlot.PlotGraphics(self.MainLines,'',xlabel,'Current, A')
		self.MainDraw.Draw(self.MainGraph)

	
	def FrameClose(self, event):
		command = Command('EXIT', [])
		self.CommandServer.CommandQueue.put(command)
		self.Destroy()


	def SelectDir(self, TextCtrl):		
		with wx.DirDialog(	self, "Choose directory", "", style = wx.DD_DEFAULT_STYLE) as dirDialog:
			if dirDialog.ShowModal() != wx.ID_CANCEL:
				pathname = dirDialog.GetPath()
				TextCtrl.Value = pathname
				print(pathname)
				
		wx.CallLater(1000,self.FileName.SetFocus)
		
		
	def onSelectDir(self, event):
				self.SelectDir(self.SaveDir)
		
		
		
	def onChannelChange(self, event):
		button = event.GetEventObject()
		Channel = button.Id // 100
		Select  = button.Id % 100
		State   = True
		
		if Channel!=5:
			State = button.GetValue()
			group = Channel*100
			[wx.FindWindowById(group+num,self).SetValue(0) for num in range(1,5) if num!=Select]
		else:
			[[wx.FindWindowById(group*100+num,self).SetValue(0) for num in range(1,5)] for group in range(1,5)]
		
		
		command = Command('CHANNEL', [Channel, Select, State])
		self.CommandServer.CommandQueue.put(command)
		
		# ~ if self.CommandBuffer['busy']: return
		# ~ self.CommandBuffer['comm'] = 'CHANNEL'
		# ~ self.CommandBuffer['args'] = [Channel, Select, State]
		# ~ self.CommandBuffer['busy'] = 1
				
	def onInputChange(self, event):
		slider = event.GetEventObject()
		state = slider.GetValue()
		
		self.CommandServer.CommandQueue.put(Command('INPUT', [state]))
		
		
		# ~ if self.CommandBuffer['busy']: return 
		# ~ self.CommandBuffer['comm'] = 'INPUT'
		# ~ self.CommandBuffer['args'] = [state]
		# ~ self.CommandBuffer['busy'] = 1
		
		self.MeterTextFront.SetLabel('Front')
		self.MeterTextRear.SetLabel('Rear')
		if state:
			self.MeterTextRear.SetLabelMarkup("<span foreground='red'>Rear</span>")
		else:
			self.MeterTextFront.SetLabelMarkup("<span foreground='red'>Front</span>")
			
	def onChangeIncrement(self, event):
		state = event.GetEventObject().Value
		if state: self.IncrementSuffix.Enable()
		else: self.IncrementSuffix.Disable()
				
		
	def onCurveCheck(self, event):
		self.GraphRedraw()
				
	
	def onChangeCurveModifier(self, event):
		self.GraphRedraw()
				
	
	def onLoadFile(self, event):
		with wx.FileDialog(	self, "Load a file", "", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL: return
			pathnames = fileDialog.GetPaths()
		
		for pathname in pathnames:
			filename = 'OLD_'+os.path.basename(pathname)
			is_repeat = int(filename in list(self.DataTables.keys()))
			current_colour = self.Colors[(self.AllCurvesList.Count - is_repeat)  % len(self.Colors)]
			try:
				table = np.genfromtxt(pathname)[:,0:2]
				current_line = wxPlot.PolyLine(table, colour=current_colour, width=3, style=wx.PENSTYLE_SHORT_DASH)
				self.DataTables[filename] = CurvesItem(current_line)
				self.AllCurvesList.Insert(filename,0)
				self.AllCurvesList.Check(0)
			except:
				pass
		
		self.GraphRedraw()
				
	
	def onClearCurves(self, event):
		self.DataTables.clear()
		self.AllCurvesList.Clear()
		self.GraphRedraw()
		
	
	def onNumCorrection(self, event):
		print('onNumCorrection')
		TextCtrl = event.GetEventObject()
		value = TextCtrl.GetValue()
		newval = ''.join([char for char in value if char in '0123456789.+-e'])
		# ~ print(value, newval)
		# ~ expcont = [ichar for ichar,char in enumerate(newval) if char=='e']
		# ~ if len(expcont)>2: newval = ''.join([char for ichar,char in enumerate(newval) if ichar not in expcont[1:]])
		# ~ if len(expcont):
			# ~ pointcont = [ichar+expcont[0] for ichar,char in enumerate(newval[expcont[0]:]) if char=='.']
			# ~ newval = ''.join([char for ichar,char in enumerate(newval) if ichar not in pointcont])
		# ~ if len(newval) and newval[-1] in ['e','-','+']: newval+='0'
		# ~ try:
			# ~ val = float(newval)
		# ~ except:
			# ~ val = 0.0
		# ~ outval = '%.2f' % val
		# ~ if val and abs(val)<0.01:
			# ~ outval = '%.2e' % val
		
		
		if value!=newval: TextCtrl.ChangeValue(newval)
				
		
	def onNumKillFocus(self, event):
		TextCtrl = event.GetEventObject()
		value = TextCtrl.GetValue()
		try:
			val = float(value)
		except:
			val = 0.0
		outval = '%.2f' % val
		if val and abs(val)<0.01:
			outval = '%.2e' % val
		TextCtrl.Value = outval
		# ~ self.IV_panel.SetFocus()
		event.Skip()
				
	
	def onModeChanged(self, event):
		print('Mode changed')
		mode = event.GetEventObject().Selection
		self.FileName.Value = self.lastFilenames[mode]
		self.GraphRedraw()
	
	def onFilenameUpdate(self, event):
		self.lastFilenames[self.ModeNB.Selection] = event.GetEventObject().Value
	
	
	def onIV_Run(self, event):
		print('IV_Run')
		
		if not self.SaveDir.GetLineText(0): self.SelectDir(self.SaveDir)
		if not self.SaveDir.GetLineText(0): return
		
		if self.CommandServer.BUSY: return
		
		minV    = float(self.IV_minV.Value)
		deltaV  = float(self.IV_deltaV.Value)
		maxV    = float(self.IV_maxV.Value)
		currLim = float(self.IV_CurrLim.Value)
		
		cycling = int(self.IV_Cycle.Value)
		isUpDown = self.IV_UpDownFlag.Value
		
		command = Command('IV', [minV,maxV,deltaV,currLim,cycling,isUpDown])
		self.CommandServer.CommandQueue.put(command)
		
				
	def onIT_Run(self, event):
		print('IT_Run')
		
		if not self.SaveDir.GetLineText(0): self.SelectDir(self.SaveDir)
		if not self.SaveDir.GetLineText(0): return
		
		if self.CommandServer.BUSY:	return
		dT      = abs(float(self.IT_dT.Value))
		endT    = abs(float(self.IT_endT.Value))
		Voltage = float(self.IT_Voltage.Value)
		currLim = float(self.IT_CurrLim.Value)
		
		command = Command('IT', [dT,endT,Voltage,currLim])
		self.CommandServer.CommandQueue.put(command)


	def onMEM_Run(self, event):
		if not self.SaveDir.GetLineText(0): self.SelectDir(self.SaveDir)
		if not self.SaveDir.GetLineText(0): return
		
		if self.CommandServer.BUSY:	return
		
		args = []
		
		args.append(float(self.MEM_SetV.Value))			# 0
		args.append(float(self.MEM_SetT.Value))			# 1
		args.append(float(self.MEM_SetP.Value))			# 2
		args.append(float(self.MEM_ClearV.Value))		# 3
		args.append(float(self.MEM_ClearT.Value))		# 4
		args.append(float(self.MEM_ClearP.Value))		# 5
		args.append(float(self.MEM_ReadV.Value))		# 6
		args.append(float(self.MEM_ReadT.Value))		# 7
		args.append(float(self.MEM_ReadP.Value))		# 8
		args.append(  int(self.MEM_ReadCycles.Value))	# 9
		args.append(  int(self.MEM_TotCycles.Value))	# 10
		args.append(float(self.IT_CurrLim.Value))		# 11
		
		command = Command('MEM', args)
		self.CommandServer.CommandQueue.put(command)
		
		
	def onStop( self, event ):
		print('onStop')
		self.CommandServer.STOP = True
		self.CommandServer.CommandQueue.put(Command('EMPTY', []))
	
				
	
	


def main():
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
