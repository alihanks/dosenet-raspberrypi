
#!/usr/bin/env/python
import Tkinter
import weather_DAQ
import air_quality_DAQ
import adc_DAQ
import plot_manager_D3S
from multiprocessing import Process, Manager, Pool

# pressure, temp, humidity, co2, air, spectra, waterfall
plot_jobs = [None, None, None, None, None, None, None]

def close(index):
    global wdaq
    global adcdaq
    global mgrD3S
    global aqdaq
    if index == 0:
        wdaq.close(3)
    if index == 1:
        wdaq.close(1)
    if index == 2:
        wdaq.close(2)
    if index == 3:
        adcdaq.close(1)
    if index == 4:
        aqdaq.close(1)
    if index == 5:
        mgrD3S.close(1)
    if index == 6:
        mgrD3S.close(2)

mgrD3S = plot_manager_D3S.Manager_D3S(plot = False)

top = Tkinter.Tk()
top.geometry("800x400")
varAir = Tkinter.BooleanVar()
vard3s = Tkinter.BooleanVar()
varCO2 = Tkinter.BooleanVar()
varWeather = Tkinter.BooleanVar()


def make_run_gui():
    top1 = Tkinter.Tk()
    top1.geometry('+0+390')
    global job1
    global jobd3s
    jobd3s = None
    
    def check_plots(index):
        global plot_jobs
        for i in range(len(plot_jobs)):
            if plot_jobs[i] is not None:
                if i != index:
                    #cancel job, close graph
                    top1.after_cancel(plot_jobs[i])
                    plot_jobs[i] = None
                    close(i)
                    
    def start_D3S():
        global argq
        if vard3s.get():
            mgrD3S.run(argq)


    def start():        
        global job1
        global jobd3s 
        global wdaq
        global adcdaq
        global mgrD3S
        global aqdaq
        global argq
        if jobd3s is None:
            manager = Manager()
            argq = manager.list()
            jobd3s = Process(target=start_D3S, args=()) 
            try:
                jobd3s.start()
            except:
                print("Error: Failed to start D3S")
        if varWeather.get(): 
            wdaq.start()
        if varAir.get():
            aqdaq.start()
        if varCO2.get():
            adcdaq.start()                
        job1=top1.after(1000,start)

    def stop():
        global jobd3s
        global job1
        if jobd3s is not None:
            mgrD3S.takedown()
        top1.after_cancel(job1)
        jobd3s = None
        check_plots(-1)

    def press(): 
        global wdaq
        global plot_jobs
        check_plots(0)
        wdaq.press()
        plot_jobs[0]=top1.after(1000,press)
        
    def temp():
        global wdaq
        global plot_jobs
        check_plots(1)
        wdaq.temp()
        plot_jobs[1]=top1.after(1000,temp)
        
    def humid():
        global wdaq
        global plot_jobs
        check_plots(2)
        wdaq.humid()
        plot_jobs[2]=top1.after(1000,humid)
        
    def CO2():
        global adcdaq
        global plot_jobs
        check_plots(3)
        adcdaq.plot_CO2()
        plot_jobs[3]=top1.after(1000,CO2)
        
    def airquality():
        global aqdaq
        global plot_jobs
        check_plots(4)
        aqdaq.pmplot()
        plot_jobs[4]=top1.after(1000,airquality)

    def multiprocess(a,b):
        a
        b

    def D3S_spectra():
        global argq
        global mgrD3S
        global plot_jobs
        check_plots(5)
        p = Pool(processes = 2)
        p.map(multiprocess, [mgrD3S.plot_spectrum(2,argq), start_D3S()])
        plot_jobs[5]=top1.after(1000,D3S_spectra)
        
    def D3S_waterfall():
        global mgrD3S
        global plot_jobs
        check_plots(6)
        mgrD3S.plot_waterfall(1)
        plot_jobs[6]=top1.after(1000,D3S_waterfall)


    startButton1 = Tkinter.Button(top1, height=2, width=10, text ="Start", command = start)
    stopButton1 = Tkinter.Button(top1, height=2, width=10, text ="Stop", command = stop)
    startButton1.grid(row=0, column=0)
    stopButton1.grid(row=0, column=1)

    if varWeather.get():
        PressureButton = Tkinter.Button(top1, height=2, width=10, text = "Pressure", command = press)
        PressureButton.grid(row=0, column=2)
        TempButton = Tkinter.Button(top1, height=2, width=10, text = "Temperature", command = temp)
        TempButton.grid(row=0, column=3)
        HumidButton = Tkinter.Button(top1, height=2, width=10, text = "Humidity", command = humid)
        HumidButton.grid(row=0, column=4)

    if varCO2.get():
        CO2Button = Tkinter.Button(top1, height=2, width=10, text = "CO2", command = CO2)
        CO2Button.grid(row=0, column=5)
        
    if varAir.get():
        AirButton = Tkinter.Button(top1, height=2, width=10, text = "Air Quality", command = airquality)
        AirButton.grid(row=0, column=6)
       
    if vard3s.get():
        d3sButton_spectra = Tkinter.Button(top1, height=2, width=10, text = "D3S Spectra", command = D3S_spectra )
        d3sButton_spectra.grid(row=0, column=7)
        d3sButton_waterfall = Tkinter.Button(top1, height=2, width=10, text = "D3S Waterfall", command = D3S_waterfall)
        d3sButton_waterfall.grid(row=0, column=8)

    
    top1.attributes("-topmost", True)
    top1.mainloop()

def weather_test():
    if varCO2.get(): 
        global adcdaq
        adcdaq = adc_DAQ.adc_DAQ()
        print("create CO2 file")
        adcdaq.create_file()
    if varAir.get(): 
        global aqdaq
        aqdaq = air_quality_DAQ.air_quality_DAQ()
        print("create Air file")
        aqdaq.create_file()
    if varWeather.get(): 
        global wdaq
        wdaq = weather_DAQ.weather_DAQ()
        print("create weather file")
        wdaq.create_file()

    make_run_gui() 
  

AirButton = Tkinter.Checkbutton(top, text="Air Quality", variable=varAir, height=2, width=2, font="Times 25")    
WeatherButton = Tkinter.Checkbutton(top, text='Weather Sensor', variable=varWeather, font="Times 25", height=2, width=2)
CO2Button = Tkinter.Checkbutton(top, text="CO2 Sensor", variable=varCO2, font="Times 25", height=2, width=2)
d3sButton = Tkinter.Checkbutton(top, text="D3S", variable=vard3s, font="Times 25", height=2, width=2)
RecordButton = Tkinter.Button(top, text="Record Data", height=2, width=20, command = weather_test, font="Times 25")  

AirButton.pack(fill ='both')   
WeatherButton.pack(fill = 'both')
CO2Button.pack(fill ='both')
d3sButton.pack(fill = 'both')
RecordButton.pack(fill = 'both')
    
top.mainloop()
