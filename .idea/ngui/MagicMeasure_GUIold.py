# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.lib.plot as wxPlot



###########################################################################
## Class MainFrameGUI
###########################################################################

class MainFrameGUI ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE|wx.TAB_TRAVERSAL, name = u"MagicMeasure" )

		self.SetSizeHints( wx.Size( 1024,768 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		fgSizer1 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.Point( -1,-1 ), wx.Size( 950,-1 ), 0 )
		self.GraphPanel = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		self.MainDraw=wxPlot.PlotCanvas(self.GraphPanel)
		self.MainDraw.enableZoom=True
		bSizer4.Add( self.MainDraw, 1, wx.ALL|wx.EXPAND, 5 )


		self.GraphPanel.SetSizer( bSizer4 )
		self.GraphPanel.Layout()
		bSizer4.Fit( self.GraphPanel )
		self.m_notebook1.AddPage( self.GraphPanel, u"Main", False )
		self.ResistancePanel = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer41 = wx.BoxSizer( wx.VERTICAL )

		self.ResistanceDraw=wxPlot.PlotCanvas(self.ResistancePanel)
		self.ResistanceDraw.enableZoom=True
		bSizer41.Add( self.ResistanceDraw, 1, wx.ALL|wx.EXPAND, 5 )


		self.ResistancePanel.SetSizer( bSizer41 )
		self.ResistancePanel.Layout()
		bSizer41.Fit( self.ResistancePanel )
		self.m_notebook1.AddPage( self.ResistancePanel, u"Resistance", False )
		self.ResistanceLgPanel = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer42 = wx.BoxSizer( wx.VERTICAL )

		self.ResistanceLgDraw=wxPlot.PlotCanvas(self.ResistanceLgPanel)
		self.ResistanceLgDraw.enableZoom=True
		bSizer42.Add( self.ResistanceLgDraw, 1, wx.ALL|wx.EXPAND, 5 )


		self.ResistanceLgPanel.SetSizer( bSizer42 )
		self.ResistanceLgPanel.Layout()
		bSizer42.Fit( self.ResistanceLgPanel )
		self.m_notebook1.AddPage( self.ResistanceLgPanel, u"lg(Resistance)", False )

		fgSizer1.Add( self.m_notebook1, 0, wx.ALL|wx.EXPAND, 5 )

		self.SettingsPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), wx.TAB_TRAVERSAL )
		SettingsSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
		SettingsSizer.SetFlexibleDirection( wx.BOTH )
		SettingsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_notebook3 = wx.Notebook( self.SettingsPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.PresetSettingsPanel = wx.Panel( self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		PresetSettingsSizer = wx.StaticBoxSizer( wx.StaticBox( self.PresetSettingsPanel, wx.ID_ANY, u"Presets" ), wx.VERTICAL )

		fgSizer12 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		sbSizer15 = wx.StaticBoxSizer( wx.StaticBox( PresetSettingsSizer.GetStaticBox(), wx.ID_ANY, u"Connectors" ), wx.VERTICAL )

		fgSizer5 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( sbSizer15.GetStaticBox(), wx.ID_ANY, u"Left tip/table" ), wx.VERTICAL )

		RL_sizer = wx.GridSizer( 3, 3, 0, 0 )

		self.m_staticText1 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		RL_sizer.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.m_staticText2 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"4W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		RL_sizer.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.m_staticText3 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"2W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		RL_sizer.Add( self.m_staticText3, 0, wx.ALL, 5 )

		self.m_staticText4 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		self.m_staticText4.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.m_staticText4.SetForegroundColour( wx.Colour( 255, 0, 0 ) )

		RL_sizer.Add( self.m_staticText4, 0, wx.ALL, 5 )

		self.RL_4W_pos = wx.CheckBox( sbSizer11.GetStaticBox(), 303, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer.Add( self.RL_4W_pos, 0, wx.ALL, 5 )

		self.RL_2W_pos = wx.CheckBox( sbSizer11.GetStaticBox(), 301, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer.Add( self.RL_2W_pos, 0, wx.ALL, 5 )

		self.m_staticText5 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"–", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )

		self.m_staticText5.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.m_staticText5.SetForegroundColour( wx.Colour( 0, 0, 255 ) )

		RL_sizer.Add( self.m_staticText5, 0, wx.ALL, 5 )

		self.RL_4W_neg = wx.CheckBox( sbSizer11.GetStaticBox(), 304, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer.Add( self.RL_4W_neg, 0, wx.ALL, 5 )

		self.RL_2W_neg = wx.CheckBox( sbSizer11.GetStaticBox(), 302, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer.Add( self.RL_2W_neg, 0, wx.ALL, 5 )


		sbSizer11.Add( RL_sizer, 1, wx.EXPAND, 5 )


		fgSizer5.Add( sbSizer11, 1, wx.EXPAND, 5 )

		sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( sbSizer15.GetStaticBox(), wx.ID_ANY, u"Right tip/table" ), wx.VERTICAL )

		RL_sizer1 = wx.GridSizer( 3, 3, 0, 0 )

		self.m_staticText11 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )

		RL_sizer1.Add( self.m_staticText11, 0, wx.ALL, 5 )

		self.m_staticText21 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"4W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText21.Wrap( -1 )

		RL_sizer1.Add( self.m_staticText21, 0, wx.ALL, 5 )

		self.m_staticText31 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"2W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )

		RL_sizer1.Add( self.m_staticText31, 0, wx.ALL, 5 )

		self.m_staticText41 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText41.Wrap( -1 )

		self.m_staticText41.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.m_staticText41.SetForegroundColour( wx.Colour( 255, 0, 0 ) )

		RL_sizer1.Add( self.m_staticText41, 0, wx.ALL, 5 )

		self.RR_4W_pos = wx.CheckBox( sbSizer12.GetStaticBox(), 403, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer1.Add( self.RR_4W_pos, 0, wx.ALL, 5 )

		self.RR_2W_pos = wx.CheckBox( sbSizer12.GetStaticBox(), 401, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer1.Add( self.RR_2W_pos, 0, wx.ALL, 5 )

		self.m_staticText51 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"–", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText51.Wrap( -1 )

		self.m_staticText51.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.m_staticText51.SetForegroundColour( wx.Colour( 0, 0, 255 ) )

		RL_sizer1.Add( self.m_staticText51, 0, wx.ALL, 5 )

		self.RR_4W_neg = wx.CheckBox( sbSizer12.GetStaticBox(), 404, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer1.Add( self.RR_4W_neg, 0, wx.ALL, 5 )

		self.RR_2W_neg = wx.CheckBox( sbSizer12.GetStaticBox(), 402, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer1.Add( self.RR_2W_neg, 0, wx.ALL, 5 )


		sbSizer12.Add( RL_sizer1, 1, wx.EXPAND, 5 )


		fgSizer5.Add( sbSizer12, 1, wx.EXPAND, 5 )

		sbSizer13 = wx.StaticBoxSizer( wx.StaticBox( sbSizer15.GetStaticBox(), wx.ID_ANY, u"Left tip" ), wx.VERTICAL )

		RL_sizer2 = wx.GridSizer( 3, 3, 0, 0 )

		self.m_staticText12 = wx.StaticText( sbSizer13.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )

		RL_sizer2.Add( self.m_staticText12, 0, wx.ALL, 5 )

		self.m_staticText22 = wx.StaticText( sbSizer13.GetStaticBox(), wx.ID_ANY, u"4W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText22.Wrap( -1 )

		RL_sizer2.Add( self.m_staticText22, 0, wx.ALL, 5 )

		self.m_staticText32 = wx.StaticText( sbSizer13.GetStaticBox(), wx.ID_ANY, u"2W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText32.Wrap( -1 )

		RL_sizer2.Add( self.m_staticText32, 0, wx.ALL, 5 )

		self.m_staticText42 = wx.StaticText( sbSizer13.GetStaticBox(), wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText42.Wrap( -1 )

		self.m_staticText42.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.m_staticText42.SetForegroundColour( wx.Colour( 255, 0, 0 ) )

		RL_sizer2.Add( self.m_staticText42, 0, wx.ALL, 5 )

		self.FL_4W_pos = wx.CheckBox( sbSizer13.GetStaticBox(), 103, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer2.Add( self.FL_4W_pos, 0, wx.ALL, 5 )

		self.FL_2W_pos = wx.CheckBox( sbSizer13.GetStaticBox(), 101, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer2.Add( self.FL_2W_pos, 0, wx.ALL, 5 )

		self.m_staticText52 = wx.StaticText( sbSizer13.GetStaticBox(), wx.ID_ANY, u"–", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText52.Wrap( -1 )

		self.m_staticText52.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.m_staticText52.SetForegroundColour( wx.Colour( 0, 0, 255 ) )

		RL_sizer2.Add( self.m_staticText52, 0, wx.ALL, 5 )

		self.FL_4W_neg = wx.CheckBox( sbSizer13.GetStaticBox(), 104, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer2.Add( self.FL_4W_neg, 0, wx.ALL, 5 )

		self.FL_2W_neg = wx.CheckBox( sbSizer13.GetStaticBox(), 102, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer2.Add( self.FL_2W_neg, 0, wx.ALL, 5 )


		sbSizer13.Add( RL_sizer2, 1, wx.EXPAND, 5 )


		fgSizer5.Add( sbSizer13, 1, wx.EXPAND, 5 )

		sbSizer14 = wx.StaticBoxSizer( wx.StaticBox( sbSizer15.GetStaticBox(), wx.ID_ANY, u"Right tip" ), wx.VERTICAL )

		RL_sizer3 = wx.GridSizer( 3, 3, 0, 0 )

		self.m_staticText13 = wx.StaticText( sbSizer14.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )

		RL_sizer3.Add( self.m_staticText13, 0, wx.ALL, 5 )

		self.m_staticText23 = wx.StaticText( sbSizer14.GetStaticBox(), wx.ID_ANY, u"4W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText23.Wrap( -1 )

		RL_sizer3.Add( self.m_staticText23, 0, wx.ALL, 5 )

		self.m_staticText33 = wx.StaticText( sbSizer14.GetStaticBox(), wx.ID_ANY, u"2W", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText33.Wrap( -1 )

		RL_sizer3.Add( self.m_staticText33, 0, wx.ALL, 5 )

		self.m_staticText43 = wx.StaticText( sbSizer14.GetStaticBox(), wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText43.Wrap( -1 )

		self.m_staticText43.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial" ) )
		self.m_staticText43.SetForegroundColour( wx.Colour( 255, 0, 0 ) )

		RL_sizer3.Add( self.m_staticText43, 0, wx.ALL, 5 )

		self.FR_4W_pos = wx.CheckBox( sbSizer14.GetStaticBox(), 203, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer3.Add( self.FR_4W_pos, 0, wx.ALL, 5 )

		self.FR_2W_pos = wx.CheckBox( sbSizer14.GetStaticBox(), 201, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer3.Add( self.FR_2W_pos, 0, wx.ALL, 5 )

		self.m_staticText53 = wx.StaticText( sbSizer14.GetStaticBox(), wx.ID_ANY, u"–", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText53.Wrap( -1 )

		self.m_staticText53.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.m_staticText53.SetForegroundColour( wx.Colour( 0, 0, 255 ) )

		RL_sizer3.Add( self.m_staticText53, 0, wx.ALL, 5 )

		self.FR_4W_neg = wx.CheckBox( sbSizer14.GetStaticBox(), 204, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer3.Add( self.FR_4W_neg, 0, wx.ALL, 5 )

		self.FR_2W_neg = wx.CheckBox( sbSizer14.GetStaticBox(), 202, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		RL_sizer3.Add( self.FR_2W_neg, 0, wx.ALL, 5 )


		sbSizer14.Add( RL_sizer3, 1, wx.EXPAND, 5 )


		fgSizer5.Add( sbSizer14, 1, wx.EXPAND, 5 )


		sbSizer15.Add( fgSizer5, 1, wx.EXPAND, 5 )

		self.ChannelsOff = wx.Button( sbSizer15.GetStaticBox(), 500, u"UnLink", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer15.Add( self.ChannelsOff, 0, wx.ALL|wx.EXPAND, 5 )


		fgSizer12.Add( sbSizer15, 1, wx.EXPAND, 5 )

		sbSizer16 = wx.StaticBoxSizer( wx.StaticBox( PresetSettingsSizer.GetStaticBox(), wx.ID_ANY, u"Input" ), wx.VERTICAL )

		self.MeterTextRear = wx.StaticText( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Rear", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.MeterTextRear.Wrap( -1 )

		self.MeterTextRear.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.MeterTextRear.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )

		sbSizer16.Add( self.MeterTextRear, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.InputSlider = wx.Slider( sbSizer16.GetStaticBox(), wx.ID_ANY, 1, 0, 1, wx.DefaultPosition, wx.DefaultSize, wx.SL_BOTH|wx.SL_INVERSE|wx.SL_VERTICAL )
		sbSizer16.Add( self.InputSlider, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.MeterTextFront = wx.StaticText( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Front", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.MeterTextFront.Wrap( -1 )

		self.MeterTextFront.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.MeterTextFront.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )

		sbSizer16.Add( self.MeterTextFront, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


		fgSizer12.Add( sbSizer16, 1, wx.EXPAND|wx.ALIGN_RIGHT, 5 )


		PresetSettingsSizer.Add( fgSizer12, 1, wx.EXPAND, 5 )


		self.PresetSettingsPanel.SetSizer( PresetSettingsSizer )
		self.PresetSettingsPanel.Layout()
		PresetSettingsSizer.Fit( self.PresetSettingsPanel )
		self.m_notebook3.AddPage( self.PresetSettingsPanel, u"Presets", False )
		self.m_panel13 = wx.Panel( self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel13.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		gSizer5 = wx.GridSizer( 2, 3, 0, 0 )

		PortSelectorChoices = []
		self.PortSelector = wx.ComboBox( self.m_panel13, wx.ID_ANY, u"Port selection", wx.DefaultPosition, wx.DefaultSize, PortSelectorChoices, 0 )
		gSizer5.Add( self.PortSelector, 0, wx.ALL, 5 )

		self.ScanPorts = wx.Button( self.m_panel13, wx.ID_ANY, u"SCAN", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.ScanPorts, 0, wx.ALL, 5 )

		self.StatusLabel = wx.StaticText( self.m_panel13, wx.ID_ANY, u"Not Connected", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.StatusLabel.Wrap( -1 )

		self.StatusLabel.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True, wx.EmptyString ) )
		self.StatusLabel.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNSHADOW ) )
		self.StatusLabel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		gSizer5.Add( self.StatusLabel, 0, wx.ALL, 5 )


		self.m_panel13.SetSizer( gSizer5 )
		self.m_panel13.Layout()
		gSizer5.Fit( self.m_panel13 )
		self.m_notebook3.AddPage( self.m_panel13, u"selection", True )

		SettingsSizer.Add( self.m_notebook3, 1, wx.EXPAND |wx.ALL, 5 )

		self.SavingPanel = wx.Panel( self.SettingsPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		SavingSizer = wx.StaticBoxSizer( wx.StaticBox( self.SavingPanel, wx.ID_ANY, u"Saving parameters" ), wx.VERTICAL )

		fgSizer11 = wx.FlexGridSizer( 2, 3, 0, 0 )
		fgSizer11.SetFlexibleDirection( wx.BOTH )
		fgSizer11.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText35 = wx.StaticText( SavingSizer.GetStaticBox(), wx.ID_ANY, u"Dir", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText35.Wrap( -1 )

		fgSizer11.Add( self.m_staticText35, 0, wx.ALL, 5 )

		self.SaveDir = wx.TextCtrl( SavingSizer.GetStaticBox(), wx.ID_ANY, u"/home/user/Measurements/", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		fgSizer11.Add( self.SaveDir, 1, wx.ALL|wx.EXPAND, 5 )

		self.InctementModifier = wx.CheckBox( SavingSizer.GetStaticBox(), wx.ID_ANY, u"Increment", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.InctementModifier.SetValue(True)
		fgSizer11.Add( self.InctementModifier, 0, wx.ALL, 5 )

		self.m_staticText36 = wx.StaticText( SavingSizer.GetStaticBox(), wx.ID_ANY, u"File", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText36.Wrap( -1 )

		fgSizer11.Add( self.m_staticText36, 0, wx.ALL, 5 )

		self.FileName = wx.TextCtrl( SavingSizer.GetStaticBox(), wx.ID_ANY, u"IV_meas", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer11.Add( self.FileName, 1, wx.ALL|wx.EXPAND, 5 )

		self.IncrementSuffix = wx.SpinCtrlDouble( SavingSizer.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 9999, 1.000000, 1 )
		self.IncrementSuffix.SetDigits( 0 )
		fgSizer11.Add( self.IncrementSuffix, 0, wx.ALL, 5 )


		SavingSizer.Add( fgSizer11, 1, wx.EXPAND, 5 )


		self.SavingPanel.SetSizer( SavingSizer )
		self.SavingPanel.Layout()
		SavingSizer.Fit( self.SavingPanel )
		SettingsSizer.Add( self.SavingPanel, 1, wx.ALL|wx.EXPAND, 0 )

		self.ModePanel = wx.Panel( self.SettingsPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		ModeSizer = wx.StaticBoxSizer( wx.StaticBox( self.ModePanel, wx.ID_ANY, u"Mode" ), wx.VERTICAL )

		self.ModeNB = wx.Notebook( ModeSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.IV_panel = wx.Panel( self.ModeNB, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		gbSizer1 = wx.GridBagSizer( 0, 0 )
		gbSizer1.SetFlexibleDirection( wx.BOTH )
		gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		sbSizer20 = wx.StaticBoxSizer( wx.StaticBox( self.IV_panel, wx.ID_ANY, u"Start V" ), wx.VERTICAL )

		self.IV_minV = wx.TextCtrl( sbSizer20.GetStaticBox(), wx.ID_ANY, u"-1.00", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer20.Add( self.IV_minV, 0, wx.ALL, 5 )


		gbSizer1.Add( sbSizer20, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer2011 = wx.StaticBoxSizer( wx.StaticBox( self.IV_panel, wx.ID_ANY, u"End V" ), wx.VERTICAL )

		self.IV_maxV = wx.TextCtrl( sbSizer2011.GetStaticBox(), wx.ID_ANY, u"1.00", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2011.Add( self.IV_maxV, 0, wx.ALL, 5 )


		gbSizer1.Add( sbSizer2011, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer201 = wx.StaticBoxSizer( wx.StaticBox( self.IV_panel, wx.ID_ANY, u"Δ V" ), wx.VERTICAL )

		self.IV_deltaV = wx.TextCtrl( sbSizer201.GetStaticBox(), wx.ID_ANY, u"0.10", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer201.Add( self.IV_deltaV, 0, wx.ALL, 5 )


		gbSizer1.Add( sbSizer201, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer131 = wx.StaticBoxSizer( wx.StaticBox( self.IV_panel, wx.ID_ANY, u"Curr.limit, A" ), wx.VERTICAL )

		self.IV_CurrLim = wx.TextCtrl( sbSizer131.GetStaticBox(), wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer131.Add( self.IV_CurrLim, 0, wx.ALL, 5 )


		gbSizer1.Add( sbSizer131, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		self.IV_MeasureBtn = wx.Button( self.IV_panel, wx.ID_ANY, u"Measure", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.IV_MeasureBtn.SetBackgroundColour( wx.Colour( 157, 244, 157 ) )

		gbSizer1.Add( self.IV_MeasureBtn, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		self.IV_StopBtn = wx.Button( self.IV_panel, wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.IV_StopBtn.SetBackgroundColour( wx.Colour( 255, 147, 15 ) )

		gbSizer1.Add( self.IV_StopBtn, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		sbSizer34 = wx.StaticBoxSizer( wx.StaticBox( self.IV_panel, wx.ID_ANY, u"Cycling" ), wx.HORIZONTAL )

		self.IV_Cycle = wx.SpinCtrlDouble( sbSizer34.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 9999, 1, 1 )
		self.IV_Cycle.SetDigits( 0 )
		sbSizer34.Add( self.IV_Cycle, 0, wx.ALL, 5 )

		self.IV_UpDownFlag = wx.CheckBox( sbSizer34.GetStaticBox(), wx.ID_ANY, u"Up-Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer34.Add( self.IV_UpDownFlag, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		gbSizer1.Add( sbSizer34, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 2 ), wx.EXPAND, 5 )


		self.IV_panel.SetSizer( gbSizer1 )
		self.IV_panel.Layout()
		gbSizer1.Fit( self.IV_panel )
		self.ModeNB.AddPage( self.IV_panel, u"I-V", False )
		self.IT_panel = wx.Panel( self.ModeNB, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		gbSizer3 = wx.GridBagSizer( 0, 0 )
		gbSizer3.SetFlexibleDirection( wx.BOTH )
		gbSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		sbSizer202 = wx.StaticBoxSizer( wx.StaticBox( self.IT_panel, wx.ID_ANY, u"Δ time, s" ), wx.VERTICAL )

		self.IT_dT = wx.TextCtrl( sbSizer202.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer202.Add( self.IT_dT, 0, wx.ALL, 5 )


		gbSizer3.Add( sbSizer202, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer20111 = wx.StaticBoxSizer( wx.StaticBox( self.IT_panel, wx.ID_ANY, u"End time, s" ), wx.HORIZONTAL )

		self.IT_endT = wx.TextCtrl( sbSizer20111.GetStaticBox(), wx.ID_ANY, u"10000", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer20111.Add( self.IT_endT, 0, wx.ALL, 5 )


		gbSizer3.Add( sbSizer20111, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer2012 = wx.StaticBoxSizer( wx.StaticBox( self.IT_panel, wx.ID_ANY, u"Volatge" ), wx.VERTICAL )

		self.IT_Voltage = wx.TextCtrl( sbSizer2012.GetStaticBox(), wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2012.Add( self.IT_Voltage, 0, wx.ALL, 5 )


		gbSizer3.Add( sbSizer2012, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer1311 = wx.StaticBoxSizer( wx.StaticBox( self.IT_panel, wx.ID_ANY, u"Curr.limit" ), wx.VERTICAL )

		self.IT_CurrLim = wx.TextCtrl( sbSizer1311.GetStaticBox(), wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer1311.Add( self.IT_CurrLim, 0, wx.ALL, 5 )


		gbSizer3.Add( sbSizer1311, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		self.IT_MeasureBtn = wx.Button( self.IT_panel, wx.ID_ANY, u"Measure", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.IT_MeasureBtn.SetBackgroundColour( wx.Colour( 157, 244, 157 ) )

		gbSizer3.Add( self.IT_MeasureBtn, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		self.IT_StopBtn = wx.Button( self.IT_panel, wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.IT_StopBtn.SetBackgroundColour( wx.Colour( 255, 147, 15 ) )

		gbSizer3.Add( self.IT_StopBtn, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )


		self.IT_panel.SetSizer( gbSizer3 )
		self.IT_panel.Layout()
		gbSizer3.Fit( self.IT_panel )
		self.ModeNB.AddPage( self.IT_panel, u"I-T", False )
		self.Mem_panel = wx.Panel( self.ModeNB, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		gbSizer31 = wx.GridBagSizer( 0, 0 )
		gbSizer31.SetFlexibleDirection( wx.BOTH )
		gbSizer31.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		sbSizer203 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Set V" ), wx.VERTICAL )

		self.MEM_SetV = wx.TextCtrl( sbSizer203.GetStaticBox(), wx.ID_ANY, u"-1.0", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer203.Add( self.MEM_SetV, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer203, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer20112 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Set time, s" ), wx.VERTICAL )

		self.MEM_SetT = wx.TextCtrl( sbSizer20112.GetStaticBox(), wx.ID_ANY, u"0.3", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer20112.Add( self.MEM_SetT, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer20112, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer201121 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Set pause, s" ), wx.VERTICAL )

		self.MEM_SetP = wx.TextCtrl( sbSizer201121.GetStaticBox(), wx.ID_ANY, u"0.5", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer201121.Add( self.MEM_SetP, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer201121, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer13121 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Clear V" ), wx.VERTICAL )

		self.MEM_ClearV = wx.TextCtrl( sbSizer13121.GetStaticBox(), wx.ID_ANY, u"1.0", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer13121.Add( self.MEM_ClearV, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer13121, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer131211 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Clear time, s" ), wx.VERTICAL )

		self.MEM_ClearT = wx.TextCtrl( sbSizer131211.GetStaticBox(), wx.ID_ANY, u"0.3", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer131211.Add( self.MEM_ClearT, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer131211, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer1312111 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Clear pause, s" ), wx.VERTICAL )

		self.MEM_ClearP = wx.TextCtrl( sbSizer1312111.GetStaticBox(), wx.ID_ANY, u"2.0", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer1312111.Add( self.MEM_ClearP, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer1312111, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer2013 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Read V" ), wx.VERTICAL )

		self.MEM_ReadV = wx.TextCtrl( sbSizer2013.GetStaticBox(), wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer2013.Add( self.MEM_ReadV, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer2013, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer1312 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Read time, s" ), wx.VERTICAL )

		self.MEM_ReadT = wx.TextCtrl( sbSizer1312.GetStaticBox(), wx.ID_ANY, u"0.5", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer1312.Add( self.MEM_ReadT, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer1312, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer13124 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Read pause, s" ), wx.VERTICAL )

		self.MEM_ReadP = wx.TextCtrl( sbSizer13124.GetStaticBox(), wx.ID_ANY, u"1.0", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer13124.Add( self.MEM_ReadP, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer13124, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer13123 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Read cycles" ), wx.VERTICAL )

		self.MEM_ReadCycles = wx.SpinCtrlDouble( sbSizer13123.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 9999, 1.000000, 1 )
		self.MEM_ReadCycles.SetDigits( 0 )
		sbSizer13123.Add( self.MEM_ReadCycles, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer13123, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer131231 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Total cycles" ), wx.VERTICAL )

		self.MEM_TotCycles = wx.SpinCtrlDouble( sbSizer131231.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 9999, 1.000000, 1 )
		self.MEM_TotCycles.SetDigits( 0 )
		sbSizer131231.Add( self.MEM_TotCycles, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer131231, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		sbSizer13122 = wx.StaticBoxSizer( wx.StaticBox( self.Mem_panel, wx.ID_ANY, u"Curr.limit, A" ), wx.VERTICAL )

		self.MEM_CurrLim = wx.TextCtrl( sbSizer13122.GetStaticBox(), wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		sbSizer13122.Add( self.MEM_CurrLim, 0, wx.ALL, 5 )


		gbSizer31.Add( sbSizer13122, wx.GBPosition( 3, 2 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.MEM_MeasureBtn = wx.Button( self.Mem_panel, wx.ID_ANY, u"Measure", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.MEM_MeasureBtn.SetBackgroundColour( wx.Colour( 157, 244, 157 ) )

		bSizer2.Add( self.MEM_MeasureBtn, 1, wx.ALL|wx.EXPAND, 2 )

		self.MEM_StopBtn = wx.Button( self.Mem_panel, wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.MEM_StopBtn.SetBackgroundColour( wx.Colour( 255, 147, 15 ) )

		bSizer2.Add( self.MEM_StopBtn, 1, wx.ALL|wx.EXPAND, 2 )


		gbSizer31.Add( bSizer2, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 3 ), wx.EXPAND, 5 )


		self.Mem_panel.SetSizer( gbSizer31 )
		self.Mem_panel.Layout()
		gbSizer31.Fit( self.Mem_panel )
		self.ModeNB.AddPage( self.Mem_panel, u"Mem", True )

		ModeSizer.Add( self.ModeNB, 1, wx.ALL|wx.EXPAND, 5 )


		self.ModePanel.SetSizer( ModeSizer )
		self.ModePanel.Layout()
		ModeSizer.Fit( self.ModePanel )
		SettingsSizer.Add( self.ModePanel, 1, wx.ALL|wx.EXPAND, 0 )

		self.NamesPanel = wx.Panel( self.SettingsPanel, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		NamesSizer = wx.StaticBoxSizer( wx.StaticBox( self.NamesPanel, wx.ID_ANY, u"Curves" ), wx.VERTICAL )

		AllCurvesListChoices = []
		self.AllCurvesList = wx.CheckListBox( NamesSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), AllCurvesListChoices, wx.LB_ALWAYS_SB|wx.LB_MULTIPLE|wx.FULL_REPAINT_ON_RESIZE )
		self.AllCurvesList.DragAcceptFiles( True )

		NamesSizer.Add( self.AllCurvesList, 1, wx.ALL|wx.EXPAND, 5 )

		fgSizer10 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer10.SetFlexibleDirection( wx.BOTH )
		fgSizer10.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.CurveModifier = wx.CheckBox( NamesSizer.GetStaticBox(), wx.ID_ANY, u"Last only", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer10.Add( self.CurveModifier, 0, wx.ALL, 5 )

		self.LoadFileButton = wx.Button( NamesSizer.GetStaticBox(), wx.ID_ANY, u"LoadFile(s)", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer10.Add( self.LoadFileButton, 0, wx.ALL, 5 )

		self.ClearAllButton = wx.Button( NamesSizer.GetStaticBox(), wx.ID_ANY, u"ClearAll", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer10.Add( self.ClearAllButton, 0, wx.ALL, 5 )


		NamesSizer.Add( fgSizer10, 0, wx.EXPAND, 5 )


		self.NamesPanel.SetSizer( NamesSizer )
		self.NamesPanel.Layout()
		NamesSizer.Fit( self.NamesPanel )
		SettingsSizer.Add( self.NamesPanel, 1, wx.ALL|wx.ALIGN_BOTTOM|wx.EXPAND, 0 )


		self.SettingsPanel.SetSizer( SettingsSizer )
		self.SettingsPanel.Layout()
		fgSizer1.Add( self.SettingsPanel, 0, wx.ALL, 5 )


		self.SetSizer( fgSizer1 )
		self.Layout()
		fgSizer1.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.FrameClose )
		self.Bind( wx.EVT_SIZE, self.onSize )
		self.RL_4W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.RL_2W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.RL_4W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.RL_2W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.RR_4W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.RR_2W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.RR_4W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.RR_2W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FL_4W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FL_2W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FL_4W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FL_2W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FR_4W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FR_2W_pos.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FR_4W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.FR_2W_neg.Bind( wx.EVT_CHECKBOX, self.onChannelChange )
		self.ChannelsOff.Bind( wx.EVT_BUTTON, self.onChannelChange )
		self.InputSlider.Bind( wx.EVT_SCROLL, self.onInputChange )
		self.PortSelector.Bind( wx.EVT_COMBOBOX, self.onPortSelected )
		self.ScanPorts.Bind( wx.EVT_BUTTON, self.onScanPorts )
		self.SaveDir.Bind( wx.EVT_LEFT_DCLICK, self.onSelectDir )
		self.InctementModifier.Bind( wx.EVT_CHECKBOX, self.onChangeIncrement )
		self.FileName.Bind( wx.EVT_TEXT, self.onFilenameUpdate )
		self.ModeNB.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onModeChanged )
		self.IV_minV.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IV_minV.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IV_maxV.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IV_maxV.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IV_deltaV.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IV_deltaV.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IV_CurrLim.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IV_CurrLim.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IV_MeasureBtn.Bind( wx.EVT_BUTTON, self.onIV_Run )
		self.IV_StopBtn.Bind( wx.EVT_BUTTON, self.onStop )
		self.IT_dT.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IT_dT.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IT_endT.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IT_endT.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IT_Voltage.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IT_Voltage.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IT_CurrLim.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.IT_CurrLim.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.IT_MeasureBtn.Bind( wx.EVT_BUTTON, self.onIT_Run )
		self.IT_StopBtn.Bind( wx.EVT_BUTTON, self.onStop )
		self.MEM_SetV.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_SetV.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_SetT.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_SetT.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_SetP.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_SetP.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_ClearV.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_ClearV.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_ClearT.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_ClearT.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_ClearP.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_ClearP.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_ReadV.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_ReadV.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_ReadT.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_ReadT.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_ReadP.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_ReadP.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_CurrLim.Bind( wx.EVT_KILL_FOCUS, self.onNumKillFocus )
		self.MEM_CurrLim.Bind( wx.EVT_TEXT, self.onNumCorrection )
		self.MEM_MeasureBtn.Bind( wx.EVT_BUTTON, self.onMEM_Run )
		self.MEM_StopBtn.Bind( wx.EVT_BUTTON, self.onStop )
		self.AllCurvesList.Bind( wx.EVT_CHECKLISTBOX, self.onCurveCheck )
		self.AllCurvesList.Bind( wx.EVT_DROP_FILES, self.onCurveDropFile )
		self.CurveModifier.Bind( wx.EVT_CHECKBOX, self.onChangeCurveModifier )
		self.LoadFileButton.Bind( wx.EVT_BUTTON, self.onLoadFile )
		self.ClearAllButton.Bind( wx.EVT_BUTTON, self.onClearCurves )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def FrameClose( self, event ):
		event.Skip()

	def onSize( self, event ):
		event.Skip()

	def onChannelChange( self, event ):
		event.Skip()

















	def onInputChange( self, event ):
		event.Skip()

	def onPortSelected( self, event ):
		event.Skip()

	def onScanPorts( self, event ):
		event.Skip()

	def onSelectDir( self, event ):
		event.Skip()

	def onChangeIncrement( self, event ):
		event.Skip()

	def onFilenameUpdate( self, event ):
		event.Skip()

	def onModeChanged( self, event ):
		event.Skip()

	def onNumKillFocus( self, event ):
		event.Skip()

	def onNumCorrection( self, event ):
		event.Skip()







	def onIV_Run( self, event ):
		event.Skip()

	def onStop( self, event ):
		event.Skip()









	def onIT_Run( self, event ):
		event.Skip()






















	def onMEM_Run( self, event ):
		event.Skip()


	def onCurveCheck( self, event ):
		event.Skip()

	def onCurveDropFile( self, event ):
		event.Skip()

	def onChangeCurveModifier( self, event ):
		event.Skip()

	def onLoadFile( self, event ):
		event.Skip()

	def onClearCurves( self, event ):
		event.Skip()


