#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time, serial, csv
import sys, glob, qdarkstyle
import thread
##########################################################
scale = 219.3310    #Escala para Kg
XCal = 0            #Calibracion 
YCal = 0.9846/0.979       #1.026/1.042  #Calibracion
area = 706.86       #Calibracion
dtang = 0.3333      #Calibracion
##########################################################
plotLen =  500		#Numero de Muestras totales
threshold = 50
ksamples = 50
msamples = plotLen/ksamples
geophone = "Out"
uData=['---.--','---.--','---.--','---.--','---.--','---.--','---.--']
uDatat =[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
tData = []
pData = []
M1=[0,0.01]
C1=[0,0]
row = 0
spcount = 0
plotType=0
Nrows = 10*60*2 #Numero de minutos x segundos x 2 muestras por segundo
spsel = 1
##########################################################

flagLog = False

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            #print "SerialPort:", port
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
        #except:
            pass
    return result

serialPorts = serial_ports()

if len(serialPorts)>=1:
    serialPort=serialPorts[0]
    print "SerialPort:", serialPort
    cPort = serial.Serial(port=serialPort,
                      baudrate=115200, 
                      timeout=1)
# plot array
def matrixInit():
    global pData
    for i in range(6):
        pData.append([0])

matrixInit()


#############################
# Grapichs Layout
#############################
app = QtGui.QApplication([])
win = QtGui.QMainWindow()
app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())

win.setWindowTitle('Corte directo para suelos friccionantes')
pg.setConfigOptions(antialias=True)

#############################
# Layout
win1 = pg.LayoutWidget()
win.setCentralWidget(win1)

fig2 = pg.PlotWidget(title='<div style="text-align: center;"><span style="color: #CCC; font-size: 11pt;">Grafico</span></div>')
fig2.setLabel(axis="left",text="Deformaciones",units="mm")
fig2.setLabel(axis="bottom",text="Tiempo",units="s")
fig2.setLabel(axis="top",text='<span style="color: #CCC; font-size: 12pt;">Esfuezo de corte vs Deformacion Horizontal</span>')
fig2.setLabel(axis="right",text='-')
fig2.setYRange(0,10.0);
fig2.setXRange(0,10.0);
fig2.showGrid(x=True, y=True)


curve1 = fig2.plot(pen=(  0,240,20),name="M1")

curve1.setData(pData[5],pData[1])


textMax = pg.TextItem(html='<div style="text-align: center;"><span style="color: #FF0; font-size: 12pt;">Presione Inicio</span></div>', anchor=(-0.3,1), angle=0, fill=(0, 0, 255, 100))
fig2.addItem(textMax)

tab1 = pg.TableWidget()
items = ["t(s)","Fx(Kg)","Dx(mm)","Dy(mm)","Ec(Kg/cm2)","dT(%)"] 
tab1.setRowCount(Nrows)
tab1.setColumnCount(6)

tab1.setHorizontalHeaderLabels(items)

softlabel = QtGui.QLabel('<div style="text-align: center;"><span style="color: #FFF; font-size: 14pt;">Corte directo para suelos friccionantes</span></div>')
loadlabel = QtGui.QLabel('<div style="text-align: center;"><span style="color: #FF0; font-size: 16pt;">Carga: %sKg</span></div>'%(uData[1]))
microlabel = QtGui.QLabel('<div style="text-align: center;"><span style="color: #FF0; font-size: 16pt;">Deformaciones: Dx(mm): %s, Dy(mm): %s</span></div>'%(uData[2],uData[3]))


plotBtn = QtGui.QPushButton('Grafico') 

speedlabel = QtGui.QLabel("Periodo:")
speedSel = QtGui.QComboBox()
speedSel.addItem('1s')
speedSel.addItem('5s')
speedSel.addItem('10s')

portlabel = QtGui.QLabel("Puerto:")
portSel = QtGui.QComboBox()
for port in serialPorts:
    portSel.addItem(port)

rstBtn = QtGui.QPushButton('Reset')
tareBtn = QtGui.QPushButton('Tara')
strstpBtn = QtGui.QPushButton('Inicio/Pausa')
saveBtn = QtGui.QPushButton('Guardar')
exitBtn = QtGui.QPushButton('Salir')



softlabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
loadlabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
microlabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
portlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
speedlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

win.showFullScreen()
win1.addWidget(softlabel,0,0,1,14)
win1.nextRow()
win1.addWidget(loadlabel,1,0,1,14)
win1.nextRow()
win1.addWidget(microlabel,2,0,1,14)
win1.nextRow()
win1.addWidget(fig2,3,0,1,7)
win1.addWidget(tab1,3,7,1,7)
win1.nextRow()
win1.addWidget(portlabel,col=0)
win1.addWidget(portSel,col=1)
win1.addWidget(speedlabel,col=4)
win1.addWidget(speedSel,col=5)
win1.addWidget(tareBtn,col=7)
win1.addWidget(rstBtn,col=8)
win1.addWidget(plotBtn,col=9)
win1.addWidget(strstpBtn,col=11)
win1.addWidget(saveBtn,col=12)
win1.addWidget(exitBtn,col=13)



def plotFvsX():
    #record: "t(s)","Fx(Kg)","Dx(mm)","Dy(mm)","Ec(Kg/cm2)","dT(%)"
    title='Esfuezo de corte vs Deformacion Horizontal'
    ylabel='Esfuezo de Corte'
    xlabel='Deformacion Horizontal'
    fig2.setLabel(axis="left",text=ylabel,units="kg/cm2")
    fig2.setLabel(axis="bottom",text=xlabel,units="%")
    fig2.setLabel(axis="top",text='<div style="text-align: center;"><span style="color: #CCC; font-size: 12pt;">%s</span></div>'%title)
    fig2.setLabel(axis="right",ntext='-')
    fig2.showGrid(x=True, y=True)
    curve1.setData(pData[5],pData[1])

def plotYvsX():
    #record: "t(s)","Fx(Kg)","Dx(mm)","Dy(mm)","Ec(Kg/cm2)","dT(%)"
    title='Deformacion Vertical vs Horizontal'
    ylabel='Deformacion Vertical'
    xlabel='Deformacion Horizontal'
    fig2.setLabel(axis="left",text=ylabel,units="mm")
    fig2.setLabel(axis="bottom",text=xlabel,units="%")
    fig2.setLabel(axis="top",text='<div style="text-align: center;"><span style="color: #CCC; font-size: 12pt;">%s</span></div>'%title)
    fig2.setLabel(axis="right",text='-')
    fig2.showGrid(x=True, y=True)
    fig2.showGrid(x=True, y=True)
    curve1.setData(pData[5],pData[3])
    
def plotXvsT():
    #record: "t(s)","Fx(Kg)","Dx(mm)","Dy(mm)","Ec(Kg/cm2)","dT(%)"
    title='Deformacion Horizontal vs Tiempo'
    ylabel='Deformacion Horizontal'
    xlabel='Tiempo'
    fig2.setLabel(axis="left",text=ylabel,units="mm")
    fig2.setLabel(axis="bottom",text=xlabel,units="s")
    fig2.setLabel(axis="top",text='<div style="text-align: center;"><span style="color: #CCC; font-size: 12pt;">%s</span></div>'%title)
    fig2.setLabel(axis="right",text='-')
    fig2.showGrid(x=True, y=True)
    fig2.showGrid(x=True, y=True)
    curve1.setData(pData[0],pData[3])

def plotXpvsT():
    #record: "t(s)","Fx(Kg)","Dx(mm)","Dy(mm)","Ec(Kg/cm2)","dT(%)"
    title='Deformacion Horizontal vs Tiempo'
    ylabel='Deformacion Horizontal'
    xlabel='Tiempo'
    fig2.setLabel(axis="left",text=ylabel,units="%")
    fig2.setLabel(axis="bottom",text=xlabel,units="s")
    fig2.setLabel(axis="top",text='<div style="text-align: center;"><span style="color: #CCC; font-size: 12pt;">%s</span></div>'%title)
    fig2.setLabel(axis="right",text='-')
    fig2.showGrid(x=True, y=True)
    fig2.showGrid(x=True, y=True)
    curve1.setData(pData[0],pData[5])
                        

def plotChanger():
    global plotType,curve1
    plotType = plotType + 1
    if plotType>3:
        plotType=0

    if plotType==0:
        plotFvsX()

    if plotType==1:
        plotYvsX()

    if plotType==2:
        plotXvsT()

    if plotType==3:
        plotXpvsT()


def startstop():
    global flagLog
    flagLog = not(flagLog)
    if flagLog:
        textMax.setHtml('<div style="text-align: center;"><span style="color: #FF0; font-size: 12pt;">... Grabando</span></div>')
    else:
        textMax.setHtml('<div style="text-align: center;"><span style="color: #FF0; font-size: 12pt;">... Pausa</span></div>')

def reset():
    global row,tData,pData,flagLog,spcount
    matrixInit()
    #if flagLog:
    #    textMax.setHtml('<div style="text-align: center;"><span style="color: #FF0; font-size: 12pt;">Presione Inicio</span></div>')
    tab1.clearContents()
    tData = []
    row=0
    spcount=0

def tare():
    global uData,uDatat
    for z in range(len(uData)):
        if z>0:
            uDatat[z] = uData[z]

def getData():
    global cPort, threshold,spsel,spcount
    global tData,uDatat,uData,row,curve1
    global plotType, flagLog
    while True:
        #try:
            outPut = cPort.readline()
            if "," in outPut:
                #record: "t(s)","Fx(Kg)","Dx(mm)","Dy(mm)","Ec(Kg/cm2)","dT(%)"
                #picket: "Fx(Kg)","Dx(mm)","Dy(mm)"
                outPut = outPut.replace('\r\n','')
                outPut = outPut+",0,0,0"
                outPut = outPut.split(',')
                if len(outPut)==6:
                    ts = "%d"%((row+1)*spsel)
                    fx = "%2.2f"%((int(outPut[0])/scale)*YCal+XCal)
                    dx = "%2.2f"%(int(outPut[1])/100.0)
                    dy = "%2.2f"%(int(outPut[2])/100.0)
                    ec = "%2.2f"%(float(fx)/area)
                    dt = "%2.2f"%(float(dx)*dtang)

                    outPut[0] = ts
                    outPut[1] = fx
                    outPut[2] = dx
                    outPut[3] = dy
                    outPut[4] = ec
                    outPut[5] = dt

                    for z in range(len(outPut)):
                        uData[z]=float(outPut[z])
                        outPut[z] = "%2.2f"%(float(outPut[z])-uDatat[z])
                    microlabel.setText('<div style="text-align: center;"><span style="color: #FF0; font-size: 16pt;">Deformaciones: Dx(mm): %s, Dy(mm): %s</span></div>'%(outPut[2],outPut[3]))
                    loadlabel.setText('<div style="text-align: center;"><span style="color: #FF0; font-size: 16pt;">Carga: %sKg</span></div>'%(outPut[1]))            
                    
                    spcount=spcount+1

                    if flagLog and (spcount>=spsel):
                        for z in range(len(outPut)):
                            newdata = QtGui.QTableWidgetItem()
                            newdata.setText(outPut[z])
                            tab1.setItem(row,z,newdata)
                            #if z<6:
                            #    pData[z].remove(pData[z][0])
                            pData[z].append(uData[z]-uDatat[z])
                        
                        if plotType==0:
                            curve1.setData(pData[5],pData[1])
                        
                        if plotType==1:
                            curve1.setData(pData[5],pData[3])
                            
                        if plotType==2:
                            curve1.setData(pData[0],pData[3])
                        
                        if plotType==3:
                            curve1.setData(pData[0],pData[5])

                        tData.append(outPut)
                        spcount=0
                        row = row+1
        #except:
        #    time.sleep(10)
        #    pass


def savecsv(self):
    path = QtGui.QFileDialog.getSaveFileName(
        parent = None, 
        caption='Guardar Archivo', 
        directory='', 
        filter='CSV(*.csv)')
    datetime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    if not path.isEmpty():
        path = path.replace(".csv","")
        with open(unicode(path.append('_%s.csv'%datetime)), 'wb') as stream:
            writer = csv.writer(stream)
            writer.writerow(['Fecha:',time.strftime("%Y/%m/%d", time.localtime())])
            writer.writerow(['Hora:',time.strftime("%H:%M:%S", time.localtime())])
            writer.writerow(["t(s)","Fx(Kg)","Dx(mm)","Dy(mm)","Ec(Kg/cm2)","dT(%)"])
            timesnap = 0
            for myrow in tData:
                #rawdata = ["%1.1f"%timesnap, myrow[0],myrow[1],myrow[2],myrow[3],myrow[4],myrow[5]]
                rawdata = [myrow[0],myrow[1],myrow[2],myrow[3],myrow[4],myrow[5]]
                writer.writerow(rawdata)
                timesnap=timesnap+.5


def portsel():
    global cPort
    serialPort = str(portSel.currentText())
    print "SerialPort:", serialPort
    cPort = serial.Serial(port=serialPort,
                  baudrate=115200, 
                  timeout=1)
    cPort.flushInput()
    cPort.flushOutput()

def speedsel():
    global spsel
    spsel =  int(speedSel.currentText().replace("s",""))
    print("spsel:%d"%spsel)

def exit():
    app.quit()


plotBtn.clicked.connect(plotChanger)
rstBtn.clicked.connect(reset)    
tareBtn.clicked.connect(tare)    
strstpBtn.clicked.connect(startstop)    
saveBtn.clicked.connect(savecsv)    
exitBtn.clicked.connect(exit)    
portSel.activated[str].connect(portsel)
speedSel.activated[str].connect(speedsel)
## Start Qt event loop unless running in interactive mode or using pyside.

thread.start_new_thread( getData, ())
QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("windowsvista"))
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

