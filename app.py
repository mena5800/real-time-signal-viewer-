import serial
import time
import plotly.express as px
import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")


def read_csv(file):
    df = pd.read_csv(file)
    signal = df.iloc[:,1].values
    return signal


def divide_samples(signal):
    avg_samples = []
    r_samples = []
    sum = 0
    max = 0
    min = 0
    for i in range(1,len(signal)):
        sum += signal[i]
        if signal[i]<min:
            min = signal[i]
        if signal[i]>max:
            max = signal[i]
        if i % 5 ==0:
            avg = sum/5
            avg_samples.append(avg)
            r_samples.append(max-min)
            max = 0
            min = 0
            sum = 0
    return avg_samples , r_samples

def get_n_samples(y):
    x = []
    for i in range(1,len(y)+1):
        x.append(i)
    return x

##-------x-chart---------##

def get_ucl_x(avg_samples,r_samples,n_samples):
    sum = 0
    sum_r = 0
    for i in range(len(avg_samples)):
        sum+= avg_samples[i]
        sum_r += r_samples[i] 
    avg_s  = sum / len(avg_samples)
    avg_r = sum_r/len(r_samples)
    #nsample = 5
    ucl = avg_s+0.58*avg_r
    cl = avg_s
    lcl = avg_s-0.58*avg_r
    return [ucl]*n_samples,[cl]*n_samples,[lcl]*n_samples

##----------r-chart-------##
def get_ucl_r(r_samples,n_samples):
    sum  = 0
    for i in r_samples:
        sum += i
    avg_r = sum/len(r_samples)
    ucl = 2.11*avg_r
    cl = avg_r
    lcl = 0*avg_r
    return [ucl]*n_samples,[cl]*n_samples,[lcl]*n_samples


if "mean" not in st.session_state:
	st.session_state.mean = [] 
	st.session_state.sample = []
	st.session_state.range = []
	

with st.sidebar:

	mode = st.radio(
		"mode",
		('csv file','real time signal'))

if mode == "real time signal":
	try:
		# set up the serial line
		ser = serial.Serial('COM7', 9600)

		time.sleep(2)

		# Read and record the data
		data =[]                       # empty list to store the data
		mean = []
		sum = 0
		placeholder1 = st.empty()
		placeholder2 = st.empty()
		max = 0
		min = 0
		for i in range(1,101):
			b = ser.readline()         # read a byte string
			string_n = b.decode()  # decode byte string into Unicode  
			string = string_n.rstrip() # remove \n and \r
			flt = int(string)   
			sum += flt
			if flt<min:
				min = flt
			if flt>max:
				max = flt

			if i % 5 ==0:
				avg = sum/5
				st.session_state.range.append(max-min)
				st.session_state.mean.append(avg)
				st.session_state.sample.append(len(st.session_state.mean))
				# fig =px.line(x =st.session_state.sample , y =st.session_state.signal)
				max = 0 
				min = 0
				sum = 0
				fig1 =plt.figure(figsize=(10, 2.5))
				plt.plot(st.session_state.sample,st.session_state.mean)
				plt.plot(st.session_state.sample,st.session_state.mean,"o")
				num = len(st.session_state.sample)
				plt.plot(st.session_state.sample,[50]*num)
				plt.plot(st.session_state.sample,[100]*num)
				plt.plot(st.session_state.sample,[150]*num)
				plt.xlabel("sample")
				plt.ylabel("mean")
				plt.legend(["line", "mean","ucl","cl","lcl"], loc=0, frameon=True)
				placeholder1.plotly_chart(fig1,use_container_width=True)

				
				fig2 = plt.figure(figsize=(10, 2.5))
				plt.plot(st.session_state.sample,st.session_state.range)
				plt.plot(st.session_state.sample,st.session_state.range,"o")
				plt.plot(st.session_state.sample,[0]*num)
				plt.plot(st.session_state.sample,[75]*num)
				plt.plot(st.session_state.sample,[150]*num)
				plt.xlabel("sample")
				plt.ylabel("range")
				plt.legend(["line", "mean","ucl","cl","lcl"], loc=0, frameon=True)
				placeholder2.plotly_chart(fig2,use_container_width=True)

				if st.session_state.mean[-1] > 150 :
					st.sidebar.error("your readings exceeds ucl")
				if st.session_state.mean[-1] <50:
					st.sidebar.error("your readings below lcl")
				

			time.sleep(0.1)            # wait (sleep) 0.1 seconds

		ser.close()
	except:
		st.write("Arduino not connected")
		

else:
	with st.sidebar:
		uploaded_file = st.file_uploader("Choose a file")
	if uploaded_file is not None:
		signal = read_csv(uploaded_file)
		avg_samples , r_samples = divide_samples(signal)
		n_samples = get_n_samples(avg_samples)
		ucl_x,cl_x,lcl_x = get_ucl_x(avg_samples,r_samples,len(n_samples))
		ucl_r,cl_r,lcl_r = get_ucl_r(r_samples,len(n_samples))

		#x-chart
		st.subheader("x-chart")
		fig1 =plt.figure(figsize=(10, 2.5))
		plt.plot(n_samples,avg_samples)
		plt.plot(n_samples,avg_samples,"o")
		plt.plot(n_samples,ucl_x)
		plt.plot(n_samples,cl_x)
		plt.plot(n_samples,lcl_x)
		plt.xlabel("sample")
		plt.ylabel("mean")
		plt.legend(["line", "mean","ucl","cl","lcl"], loc=0, frameon=True)
		st.plotly_chart(fig1,use_container_width=True)
		
		#r-chart
		st.subheader("r-chart")
		fig = plt.figure(figsize=(10, 2.5))
		plt.plot(n_samples,r_samples)
		plt.plot(n_samples,r_samples,"o")
		plt.plot(n_samples,ucl_r)
		plt.plot(n_samples,cl_r)
		plt.plot(n_samples,lcl_r)
		plt.xlabel("sample")
		plt.ylabel("range")
		plt.legend(["line", "mean","ucl","cl","lcl"], loc=0, frameon=True)
		st.plotly_chart(fig,use_container_width=True)




		

		


