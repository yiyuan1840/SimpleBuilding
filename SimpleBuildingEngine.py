##################################
#Simplified Building Model Engine#
##################################
#This is the main driver program

import pandas as pd
import datetime


#INITIALIZATION
#First, the simulation will initialize a pandas data array to contain the timestep variables
from SimpleBuilding import sbefunctionlib

print 'INITIALIZATION'

# Specify start and end datetime and timestep length
Simstart = datetime.datetime(2012,01,01,00)
Simend = datetime.datetime(2012,01,10,23)
timesteplength = datetime.timedelta(hours=1)
SimLength = Simend - Simstart
NumOfTimesteps = int(SimLength.total_seconds() / timesteplength.total_seconds())

print 'Initializing Variables'
"""
T_i - Intial Temp
T_s - Temp
T_m - Temp
T_es - Temp
T_em - Temp
T_op - Temp
T_rm - Temp
I_sol_gl - Temp
I_sol_lopw - Insolation
I_sol_hopw - Insolation
I_sol_fr -
I_sol_rf -
I_ir_h -
w_out_data - Humidity Ratio
"""
SimDataColumns = ['T_i','T_s','T_es','T_em','T_op','T_rm','I_sol_gl','I_sol_lopw','I_sol_hopw',
                  'I_sol_fr','I_sol_rf','I_ir_h','w_out_data','I_th_cs','I_th_cs2']
Timestamplist = [(Simstart + x*timesteplength) for x in range(0,NumOfTimesteps)]

#Creates a pandas dataframe with a timestamp index. Input and Output data will be pulled and pushed to this dataframe
Sim = pd.DataFrame(columns=SimDataColumns,index=Timestamplist)

#DATA
#1. MISCELLANOUS
#Dtau = 1#en h =>15 min= 0.25
#tau_1 = 1
#tau_2 = 365 * 24 / Dtau

T_m_f = -10
T_m_fd = T_m_f

#Tolerances
zero = 1E-6
error = 1E-3

#test case
Btest = 200

# fluid properties
c_a = 1006# air
c_v = 1830# steam
H_fg = 2257 * 1000#J/kg

#2. LOCATION
Lat = 39.8
Long = 104.9
Long_st = 7 * 15
#
#3. CLIMATE
#Rating conditions
print 'Loading Weather Design Data'
T_out_winter_n = -10#[C]
RH_out_winter_n = 0.9#[-]
T_out_summer_n = 30#[C]
T_i_set_h_occ = 20
RH_out_summer_n = 0.5#[-]
I_max_S = 616.5#[W/m^2]
I_max_SW = 751.6#[W/m^2]
I_max_W = 514.3#[W/m^2]
I_max_NW = 123.1#[W/m^2]
I_max_N = 116.2#[W/m^2]
I_max_NE = 116.2#[W/m^2]
I_max_E = 116.2#[W/m^2]
I_max_SE = 196.3#[W/m^2]
I_max_horiz = 800#[W/m^2]
T_out_avg = 9.7#[C]
T_i_avg = 20#[C]
albedo = 0.2#Ground albedo
I_ir_cs = -100#Clear sky to actual global radiation ratio
I_ir_cc=-45
J_cs = 1
J_cc = 0.354
"""
##Outdoor conditions
#T_out_data = xlsread(mstring('BESTTEST_DATA.xls'), mstring('D3:D8763'))
#P_out_data = xlsread(mstring('BESTTEST_DATA.xls'), mstring('H3:H8763'))
#T_wb_out_data = xlsread(mstring('BESTTEST_DATA.xls'), mstring('E3:E8763'))
#RH_out_data = xlsread(mstring('BESTTEST_DATA.xls'), mstring('G3:G8763'))
#I_glob_data = xlsread(mstring('BESTTEST_DATA.xls'), mstring('L3:L8763'))
#I_diff_data = xlsread(mstring('BESTTEST_DATA.xls'), mstring('N3:N8763'))
#I_dir_n_data = xlsread(mstring('BESTTEST_DATA.xls'), mstring('M3:M8763'))
"""

#Load the weather data from the specified weather file. The labels in this imported file will need to be consistent
#for the import to work properly with the rest of the code
print 'Loading Weather Data'
weatherfile= pd.ExcelFile('BESTTEST_DATA.xls')
weatherfilesheet = 'Feuil1'
weatherColsToImport=[3,4,6,7,11,12,13]
weatherdata = weatherfile.parse(weatherfilesheet,skiprows=[1,2],index_col=None,parse_cols=weatherColsToImport)

#4. WALLS characteristics
#Surfaces and capacity
print 'Loading Wall Characteristics'
[n_walls, f_low_diff, f_low_dir, ori, surf_az, slope, A_t, A_fl, A_lopw_t, A_hopw_t, A_gl_t, A_fr_t,
A_lopw, A_hopw, A_gl, h_cl, C_m, A_m, U_hopw, U_lopw, U_fr, U_gl] = sbefunctionlib.WALLS(Btest)

#Glazed walls: solar and shading data
p_SHGC = 3.2#(ex: 3.2. for variable SHGC)
k_solshad = 0#Fraction of the SHGC with solar shadings
f_hemis = 0.84
#convective part of direct (short wave) solar gains
if Btest < 800:
    f_sa = 0.5
else:
    f_sa = 0.2

#Repartition of SHGC
#Without solar shadings
f_sg11 = 1#part of direct (short wave) solar gains
f_sg21 = 0#part of long wave solar gains
#with solar shadings
f_sg12 = 0#part of direct (short wave) solar gains
f_sg22 = 0#part of long wave solar gains

#Note: this repartition is not the one of the RT2005. Here the gain
#due to solar transmission are supposed to be purely convective
#with solar shadings, while the factor f_sa does a ponderation
#between convection and radiation when they are no shadings.

#Heat transfer coefficients (U values)
#Convection, radiation
h_e_h = 29.3#[W/m^2-K] %winter conditions
h_e_l = 21
h_i = 8.29#[W/m^2-K]
h_is = 8.29
h_ri = 5.5
h_ci = h_is - h_ri
h_rs = 1.2 * h_ri

#5. INTERNAL GAINS
#Appliances
f_appl_c = 0.4

#Heating/Cooling system
f_h_c = 1
f_c_c = 1
Q_dot_sys = 0
#Occupancy
f_occ_c = 0
Q_dot_occ = 0
#Light
f_light_c = 0
Q_dot_light = 0
#Process
f_proc_c = 0
Q_dot_proc = 0
#Heat recovery from systems
f_recov_c = 0
Q_dot_th_recov = 0

##""""""""""""""""""""""""""""%
##CALCULATION
#
print 'CACULATION'
print 'Starting Calculation'
#Iterate through the time range using the defined timesteps
SimCurrentTimestamp = Simstart
CurrSimIndex = 0

while SimCurrentTimestamp < Simend:
    #    print 'Current Sim Timestamp is '+ Sim.index[CurrSimIndex].isoformat()
    #for tau in mslice[tau_1:tau_2]:

    #    Calculate weather data variables needed for the simulation using functions
    #    PUT THE FOLLOWING INTO THE SIMULATION
    #    w_out_data(tau).lvalue = w_t_RH(P_out_data(tau), T_out_data(tau), RH_out_data(tau))
    #    #Calendar
    #    [h_d(tau), day(tau), day_week(tau), day_year(tau), hour_week(tau), week(tau), month(tau)] = CALENDAR(zero, tau)
    #    #Global horizontal clear sky radiation
    #    [I_th_cs(tau), I_th_cs2(tau)] = CSITH(Lat, Long, Long_st, day_year(tau), tau)
    #    #Calendar
    #    n = day(tau)
    #    h = ceil(tau * Dtau)

    #Outside Humidity Ratio
    Sim.w_out_data[CurrSimIndex] = sbefunctionlib.w_t_RH(weatherdata.P_out_data[CurrSimIndex],
        weatherdata.T_out_data[CurrSimIndex],weatherdata.RH_out_data[CurrSimIndex])
    #Global horizontal clear sky radiation
    DayOfYear = SimCurrentTimestamp.timetuple().tm_yday
    HourOfYear = SimCurrentTimestamp.timetuple().tm_yday*24 + SimCurrentTimestamp.hour
    Sim.I_th_cs[CurrSimIndex], Sim.I_th_cs2[CurrSimIndex] = \
    sbefunctionlib.CSITH(Lat, Long, Long_st, DayOfYear, HourOfYear)

#    #ventilation - set points- Radiation properties - infiltration - appliances internal gain
#    Btest_cases(Btest, h_d(tau)) = [T_i_set_h, T_i_set_c, SHGC_gl_0, epsilon_ir_hopw, epsilon_ir_lopw, epsilon_ir_gl,
#                                    alpha_hopw, alpha_lopw, e_solshad, mode_solshad, NL_ext_max, IAC_solshad,
#                                    Q_dot_appl, ACH_inf, V_dot_ve]
#    V_in = h_cl * A_fl

#    T_e(tau).lvalue = T_out_data(tau)
#    P_e(tau).lvalue = P_out_data(tau)
#    T_inf(tau).lvalue = T_e(tau)
#    w_e(tau).lvalue = w_out_data(tau)
#    w_inf = w_e(tau)
#
#    #Heat transfer coefficients (H=AU values)
#
#    [v_e(tau)] = DRYAIRPROP(T_e(tau), P_e(tau))
#    rho_e(tau).lvalue = 1 / v_e(tau)
#
#    #Infiltrations
#    T_inf = T_e(tau)
#    w_inf = w_e(tau)
#    rho_inf = rho_e(tau)
#    V_dot_inf = ACH_inf * V_in * 1 / 3600
#    h_inf = h_t_w(c_a, c_v, H_fg, T_inf, w_inf)
#    m_dot_inf = V_dot_inf * rho_inf
#
#
#    # Ventilation
#    T_ve(tau).lvalue = T_e(tau)
#    w_ve(tau).lvalue = w_e(tau)
#    [v_ve] = DRYAIRPROP(T_ve(tau), P_e(tau))
#    h_ve = h_t_w(c_a, c_v, H_fg, T_ve(tau), w_ve(tau))
#    rho_ve = 1 / v_ve
#    m_dot_ve = V_dot_ve * rho_ve
#
#    #Total supply(equivalent) flow rate
#    m_dot_eq = m_dot_ve + m_dot_inf
#    w_eq = (m_dot_ve * w_ve(tau) + m_dot_inf * w_inf) / (m_dot_eq + zero)
#    h_eq = (m_dot_ve * h_ve + m_dot_inf * h_inf) / (m_dot_eq + zero)
#    T_eq = (h_eq - H_fg * w_eq) / (c_a + c_v * w_eq)
#
#    H_ei = m_dot_eq * (c_a + c_v * w_eq)
#
#    # Light walls
#    H_tr_es = sum(A_gl *elmul* U_gl + A_lopw *elmul* U_lopw + A_fr_t *elmul* U_fr)
#
#    # Massive walls
#    H_tr_is = A_t / (1 / h_ci - 1 / h_is)
#    H_tr_ms = h_is * A_m
#    H_tr_op = sum(A_hopw *elmul* U_hopw)
#    H_tr_em = 1 / (1 / H_tr_op - 1 / H_tr_ms)
#
#    # Solar gains
#    #Irradiation
#    I_glob_h = I_glob_data(tau)
#    I_diff_h = I_diff_data(tau)
#    #Infrared radiation
#    tau_h_1 = tau_1
#    tau_h_2 = tau_2 * Dtau
#    [I_ir_h(tau)] = IR_horiz(I_ir_cs, I_ir_cc, J_cs, J_cc, I_glob_data, I_th_cs, h, tau_h_1, tau_h_2)
#
#    [Q_dot_sl(tau), Q_dot_sh(tau), Q_dot_s_d_tot(tau), Q_dot_svl_tot(tau), I_tot_w(tau, mslice[:]), I_tr_tot(tau),
#     Q_dot_IR_l_tot(tau), Q_dot_IR_h_tot(tau), Q_dot_sol_l_tot(tau), Q_dot_sol_h_tot(tau), Q_dot_sol_gl_tot(tau)] = \
#    SOLARGAINS(Lat, Long, Long_st, albedo, n_walls, ori, SHGC_gl_0, p_SHGC, f_sg11, f_sg12, f_sg21, f_sg22, f_hemis,
#        A_hopw, A_lopw, A_gl, surf_az, slope, f_low_dir, f_low_diff, zero, alpha_hopw, alpha_lopw, e_solshad,
#        mode_solshad, IAC_solshad, NL_ext_max, n, h, I_glob_h, I_diff_h, I_ir_h(tau), epsilon_ir_lopw, epsilon_ir_gl,
#        epsilon_ir_hopw, U_lopw, U_gl, U_hopw, h_e_l, h_e_h)
#
#
#    # Temperatures at the nodes
#    # Equivalent outside temperatures
#    # In this version they are calculated not calculated as in the
#    # RT2005, but are "real" corrected outdoor temperatureswith (i.e.
#    # by dividing by A*(h_e_l or h_e_h) only.
#    [T_es(tau), T_em(tau)] = TEMP_OUT(error, zero, Q_dot_sl(tau), Q_dot_sh(tau), T_e(tau), H_tr_em, H_tr_es, H_tr_ms,
#        h_e_l, h_e_h, A_lopw_t, A_gl_t, A_fr_t, A_hopw_t)
#
#
#    # T_i, T_s et T_m
#    # ODE method
#    #t0=0;
#    #tf=Dtau*3600;
#    #T_m_i=T_m_f;
#    #[T_m_f,T_m(tau),T_s(tau),T_i(tau),T_op(tau),T_rm(tau) ] = TEMPODE(t0,tf,T_m_i,zero,h_ci,h_ri,T_em(tau),T_es(tau),T_ve_sup,H_ve,H_tr_is,H_tr_es,H_tr_ms,H_tr_em,C_m,Q_dot_i,Q_dot_s,Q_dot_m);
#
#
#    #Euler method
#    T_m_i = T_m_f
#    #[Q_dot_m_tot,T_m(tau),T_s(tau),T_i(tau),T_op,T_rm,T_m_f ] = TEMP( zero,h_ci,h_rs,T_em(tau),T_es(tau),
#    # T_ve_sup,H_ve,H_tr_is,H_tr_es,H_tr_ms,H_tr_em,C_m,Q_dot_i,Q_dot_s,Q_dot_m,T_m_i );
#
#    [Q_dot_hc_un(tau), Q_dot_sys(tau), T_m(tau), T_s(tau), T_i(tau), T_i_0(tau), T_m_f] = DEMAND(T_i_set_h, T_i_set_c,
#        f_sa, A_gl_t, A_t, A_fl, A_m, f_occ_c, Q_dot_occ, f_appl_c, Q_dot_appl, f_light_c, Q_dot_light, f_proc_c,
#        Q_dot_proc, Q_dot_th_recov, f_h_c, f_c_c, H_tr_es, h_is, Q_dot_svl_tot(tau), Q_dot_s_d_tot(tau), zero, h_ci,
#        h_rs, T_em(tau), T_es(tau), T_eq, H_ei, H_tr_is, H_tr_ms, H_tr_em, C_m, T_m_i)
#    #Heating
#    Q_dot_heat(tau).lvalue = max(0, Q_dot_sys(tau))
#    #Cooling
#    Q_dot_cool(tau).lvalue = min(0, Q_dot_sys(tau))
#
#
#
#
#    Q_dot_heat_stat(tau).lvalue = max(0, H_tr_op * (20 - T_e(tau)))
#
#
#t_end = toc(t_start)
#print t_end
#
#
#I_tot_S_kWhm2 = sum(I_tot_w(mslice[:], 1)) / 1000
#I_tot_W_kWhm2 = sum(I_tot_w(mslice[:], 2)) / 1000
#I_tot_N_kWhm2 = sum(I_tot_w(mslice[:], 3)) / 1000
#I_tot_E_kWhm2 = sum(I_tot_w(mslice[:], 4)) / 1000
#I_tot_H_kWhm2 = sum(I_tot_w(mslice[:], 5)) / 1000
#
#I_tr_kWhm2 = sum(I_tr_tot) / 1000
#
#I_tot_S_5march = I_tot_w(mslice[1513:1536], 1)
#I_tot_W_5march = I_tot_w(mslice[1513:1536], 2)
#I_tot_S_27july = I_tot_w(mslice[4969:4992], 1)
#I_tot_W_27july = I_tot_w(mslice[4969:4992], 2)
#
#Ti_4janFF = T_i(mslice[73:96])
#Ti_27julyFF = T_i(mslice[4969:4992])
#
#Q_dot_hc_4jan = Q_dot_sys(mslice[73:96]).cT / 1000
#Q_dot_hc_27july = Q_dot_sys(mslice[4969:4992]).cT / 1000
#
#Q_heat_kWhyr = sum(Q_dot_heat) / 1000; print Q_heat_kWhyr
#Q_cool_kWhyr = -sum(Q_dot_cool) / 1000; print Q_cool_kWhyr
#Q_dot_h_kW = max(Q_dot_heat(mslice[12:8760])) / 1000; print Q_dot_h_kW
#Q_dot_c_kW = -min(Q_dot_cool) / 1000; print Q_dot_c_kW

    SimCurrentTimestamp += timesteplength
    CurrSimIndex += 1