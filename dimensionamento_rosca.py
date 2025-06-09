import math
import streamlit as st
import pandas as pd

# Fatores VDI 2330-4-2
A1 = 0.7828
A2 = 983
A3 = 2.533
A4 = 1.192
A5 = 0.7997
A6 = 0.2827
A7 = 0.0996
A8 = 472400
A9 = 112600
A10 = 40400
A11 = 10.872

B1 = 9.522
B2 = 0.09319
B3 = 11.38
B4 = 1.915
B5 = 0.002808
B6 = 1.10910
B7 = 2.638
B8 = 0.0496
B9 = 10.339
B10 = 0.3465
B11 = 0.00499
B12 = 0.3832

def inclination_factor(inclinacao):
    C = 1 / (1 + (inclinacao / 50))
    return C

def A0_valor(inclinacao, D, N):

    if inclinacao >= 20:
        A0 = (A1 + (A2 * (inclinacao**(-A3))) - (A4 * (N**(-A5))) + (A6 * D) + (A8 * (N**(-A5)) * (inclinacao**(-A11))) - (A9 * D * (inclinacao**(-A11))))
    elif inclinacao < 20:
        A0 = 0
    return A0

def grau_de_enchimento(inclinacao, D, D_tubo, capacidade_necessaria, densidade, N, S, enchimento):

    A0 = A0_valor(inclinacao, D, N)

    Vmass = fluxo_massa(capacidade_necessaria) * densidade
    
    if inclinacao >= 20 and D > D_tubo:
        termo_a = (16*(A7 + A10 * inclinacao**(-A11))*Vmass)
        termo_b = math.pi * (D**2 - D_tubo**2) * S * N
        termo_c = 2 * (A7 + A10 * inclinacao**(-A11))
        grau_enchimento = (-A0 + math.sqrt(A0**2 + (termo_a / termo_b))) / (termo_c * 100)
    elif inclinacao < 20:
        grau_enchimento = enchimento
    return grau_enchimento

def velocidade(S, N, inclinacao):

    grau_enchimento = grau_de_enchimento(inclinacao, D, D_tubo, capacidade_necessaria, densidade, N, S, enchimento)
    A0 = A0_valor(inclinacao, D, N)
    Nmax = S * N * ( A0 * (A7 + A10 * inclinacao**(-A11)) * grau_enchimento)
    return Nmax

def fator_de_potencia(inclinacao, densidade, fm, fi):

    grau_enchimento = grau_de_enchimento(inclinacao, D, D_tubo, capacidade_necessaria, densidade, N, S, enchimento)
    fator_potencia = (B1 + B2 * inclinacao - B3 * grau_enchimento + B4 * fm + B5 * densidade + B6 * fi - (B7 + B8 * inclinacao - B9 * grau_enchimento) * N + (B10 + B11 * inclinacao - B12 * grau_enchimento) * N**2)

    return fator_potencia

def fluxo_massa(capacidade_necessaria):
    
    Vmass = capacidade_necessaria / 3600

    return Vmass

def capacidade_calculo(D, D_tubo, N, enchimento, S, inclinacao):

    N2 = N * 60
    capacidade = 47 * (D**2-D_tubo**2) * N2 * enchimento * S * (1 - (inclinacao * 4 / 100))
    
    return capacidade

def calc_potencia(L, inclinacao, capacidade_necessaria, densidade, D, S, enchimento):
    
    H = L * math.sin(inclinacao)

    if inclinacao >= 20:

        grau_enchimento = grau_de_enchimento(inclinacao, D, D_tubo, capacidade_necessaria, densidade, N, S, enchimento)
    
        fator_potencia = fator_de_potencia(inclinacao, densidade, fm, fi)

        Vmass = fluxo_massa(capacidade_necessaria)
    
        potencia = (Vmass * densidade * 9.81 * ((fator_potencia * (D / S) * L) + H)) / 1000

    elif inclinacao < 20:
        
        capacidade = capacidade_calculo(D, D_tubo, N, enchimento, S, inclinacao)

        potencia = (capacidade * (L * 6 + H) / 367) * 2.5 * 1.1 * (1 - (inclinacao * 4 / 100)) * 1.1

    return potencia

def calc_torque(potencia, N):

    potencia = calc_potencia(L, inclinacao, capacidade_necessaria, densidade, D, S, enchimento)
    ROT = N*60
    torque = potencia * 9550 / ROT
    return torque

def check_speed(S, N, inclinacao):

    A0 = A0_valor(inclinacao, D, N)

    if inclinacao >= 20:
        grau_enchimento = grau_de_enchimento(inclinacao, D, D_tubo, capacidade_necessaria, densidade, N, S, enchimento)
        Vax = S * N * (A0 + (A7 + A10 * inclinacao**(-A11) * grau_enchimento))
    elif inclinacao < 20:
        Vax = 1
    return Vax

# Streamlit

st.set_page_config(page_title="Dimensionamento de Rosca Transportadora", layout="centered")

st.title("Dimensionamento de Rosca Transportadora")

st.subheader("Parâmetros de entrada")

with st.form("input_form"):
    st.markdown("Parâmetros de entrada")
    capacidade_necessaria = st.number_input("Capacidade necessária (m³/h)", value=10.0)
    densidade = st.number_input("Densidade (kg/m³)", min_value=100.0, value=250.0)
    inclinacao = st.slider("Ângulo de inclinação (°)", 0, 90, 15)
    L = st.number_input("Comprimento da rosca (m)", value=3.0)
    D_tubo = st.number_input("Diâmetro do tubo eixo (m)", value=0.0889)
    fm = st.slider("Fator de atrito do material", 0.1, 0.7, 0.6)
    fi = st.slider("Fator de atrito interno", 0.10, 0.90, 0.54)
    enchimento = st.slider("Enchimento desejado (para ângulo < 20°)", 0.15, 0.45, 0.3)

    submitted = st.form_submit_button("Executar dimensionamento!")

if submitted:
    st.subheader("Resultados dos cálculos")

    standard_diameters = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
#    standard_diameters = [0.3]
    pitch_ratios = [0.3, 0.5, 0.8, 1.0, 1.2, 1.5]
#    pitch_ratios = [1]
    min_rpm, max_rpm = 10, 80

    C = inclination_factor(inclinacao)

    results = []
    for D in standard_diameters:
        if D > D_tubo:
            
            for pitch_ratio in pitch_ratios:
                S = D * pitch_ratio
                for RPM in range(min_rpm, max_rpm + 1, 2):
                    
                    N = RPM/60

                    grau_enchimento = grau_de_enchimento(inclinacao, D, D_tubo, capacidade_necessaria, densidade, N, S, enchimento)
                    enchimento_ok = grau_enchimento <=0.75 and grau_enchimento >=0.05
                    Vax = check_speed(S, N, inclinacao)
                    speed_ok = Vax <= 2.4 and Vax > 0
                    potencia = calc_potencia(L, inclinacao, capacidade_necessaria, densidade, D, S, enchimento)
                    potencia_ok = potencia > 0.25
                    
                    
                    if enchimento_ok and speed_ok and potencia_ok:

                        Vmass = fluxo_massa(capacidade_necessaria)
                        fator_potencia = fator_de_potencia(inclinacao, densidade, fm, fi)
                        potencia = calc_potencia(L, inclinacao, capacidade_necessaria, densidade, D, S, enchimento)
                        torque = calc_torque(potencia, N)
                        grau_enchimento = grau_de_enchimento(inclinacao, D, D_tubo, capacidade_necessaria, densidade, N, S, enchimento)
                        A0 = A0_valor(inclinacao, D, N)
                        capacidade = capacidade_calculo(D, D_tubo, N, enchimento, S, inclinacao)

                        if inclinacao >= 20:
                            Q = Vmass * 3600 / grau_enchimento
                        elif inclinacao < 20:
                            Q = capacidade
                        
                        results.append({
                            'D (m)': D,
                            'S (m)': S,
                            'N (rpm)': N*60,
                            'Torque (Nm)': torque,
                            'Potencia (kW)': potencia,
                            'Q (m3/h)': Q,
                            'Grau de enchimento': grau_enchimento,
                            })

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df.style.format(precision=2))
        best = df.sort_values(by='Potencia (kW)').iloc[0]
        st.success(
            f"Projeto mais eficiente (Menor Potência):\n\n"
            f"Diâmetro da rosca D = {best['D (m)']} m\n"
            f"Passo = {best['S (m)']:.2f} m\n"
            f"RPM = {best['N (rpm)']} rpm\n"
            f"Potência = {best['Potencia (kW)']:.2f} kW\n"
            f"Torque = {best['Torque (Nm)']:.2f} Nm\n"
            f"Grau de enchimento = {best['Grau de enchimento']}\n"
            )


        
