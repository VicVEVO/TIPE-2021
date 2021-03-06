# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 16:33:37 2021

@author: victo
"""

import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt

########################### D E F I N I T I O N S #######################

def f(x):  # la fonction définissant U[0], la température sur la barre à t = 0
    return abs(100 * np.sin(x/2) + 20)


def matrice_AB(r, taille_mat):  # calcul des deux matrices carrées A et B pour le calcul de récurrence du modèle
    #On ne les calcule qu'une fois pour réduire considérablement les calculs répétitifs inutiles

    A = np.zeros((taille_mat - 2, taille_mat - 2)) #A et B sont des matrices initialement nulles
    B = np.zeros((taille_mat - 2, taille_mat - 2)) #que en fonction de nlignes, ncolonnes utilisé à la fin
    #il faut fix le -2
    for i in range(taille_mat - 2):
        for j in range(taille_mat - 2):
            if i == j:
                A[i][j] = 2 + 2 * r
                B[i][j] = 2 - 2 * r
            elif (j == i + 1) or (i == j + 1):
                A[i][j] = -r
                B[i][j] = r
    return A,B

def init(T_int,T_ext, taille_mat):  # initialisation de la matrice U
    
    M = np.full((taille_mat, taille_mat),T_int)  #On impose T_int partout
    M[0],M[-1],M[:,0],M[:,-1] = T_ext,T_ext,T_ext,T_ext #puis on impose T_ext à l'extérieur de la boîte, donc aux extrémités de la matrice
    
    return M


def calcul_U_t_suivant(U,T_int,taille_mat,E,A,B,λ,profondeur,r):#calcule la matrice de la température U au temps suivant

    for y in range(1,taille_mat-1): #balayage de t à t+1/2: on étudie les lignes
            
        if E < y <= taille_mat - E: #on étudie le cas où on est au middle
            invA = inv(A[:E,:E])
            invAxB = np.dot(invA, B[:E,:E])
            
            U[y,:E] = calc_U(U[y,:E],invA,invAxB,r)
            U[y,taille_mat-E:] = calc_U(U[y,taille_mat-E:],invA,invAxB,r)
            
        else:
            invA = inv(A)
            invAxB = np.dot(invA, B)
            
            U[y] = calc_U(U[y],invA,invAxB,r) #calc_U(matrice 1D, CL1, CL2)
                
    for x in range(1,taille_mat-1): #balayage de t+1/2 à t+1: on étudie les colonnes
    
        if E < x <= taille_mat - E: 
            invA = inv(A[:E,:E])
            invAxB = np.dot(invA, B[:E,:E])
            
            U[:E,x] = calc_U(U[:E,x],invA,invAxB,r)
            U[taille_mat-E:,x] = calc_U(U[taille_mat-E:,x],invA,invAxB,r)
            
        else:
            invA = inv(A)
            invAxB = np.dot(invA, B)
            
            U[:,x] = calc_U(U[:,x],invA,invAxB,r)
    
    ##CALCUL DU NV T_int
        delta_T = 0
        
        for x in range(E , taille_mat-E+1): #on calcule delta T sur les bords intérieurs horizontaux
 
            delta_T += -λ*(U[E,x]-U[E-1,x])*profondeur #on étudie le bord intérieur haut
            delta_T += -λ*(U[taille_mat-E,x]-U[taille_mat-E+1,x])*profondeur #le bord intérieur bas
        
        for y in range(E, taille_mat-E+1):#pareil pour les bords intérieurs verticaux
            
            delta_T += -λ*(U[y,E]-U[y,E-1])*profondeur #on étudie le bord intérieur gauche
            delta_T += -λ*(U[y,taille_mat-E]-U[y,taille_mat-E+1])*profondeur #on étudie le bord intérieur gauche
        
        T_int += delta_T
            
    return U

def calc_U(barre,invA,invAxB,r): #T0 (resp.T1): température extérieure gauche (resp. droite)
    
    longueur = len(barre[1:-1]) # longueur de la barre où l'on change la température
    ### CALCUL DE b ###
    b = np.zeros(longueur) #ne contient pas les extrémités: 2 cases en moins
    
    b[0] = r * barre[0]
    b[-1] = 2*r * barre[-1] # on a mis 2r au lieu d'ajouter bjplus1 [longueur - 1] = r * U[longueur + 1, t]

    #il faut diminuer invAxB de 2
    barre[1:-1] = np.dot(invAxB[:longueur,:longueur], barre[1:-1]) + np.dot(invA[:longueur,:longueur],b) # application de la formule de récurrence
    return(barre)
        
########################### A F F E C T A T I O N S #######################

pas_spatial = 10**-3 #1mm
pas_temporel = 0.1 # 0.1s

L = 0.5 #longueur de la boîte (50cm)
epaisseur = 0.02 # son épaisseur (1cm)

E = int(epaisseur/pas_spatial) #conversion de l'épaisseur en nombre de points sur la matrice
taille_mat = int(L/pas_spatial) #correspond au nombre de lignes (= nb colonnes)

N_profondeur = E*100 #nombres de mesures de la profondeur de la boîte pour négliger les effets de bords

''' ########## POUR UN ORGANE ##########
ρ = 0.550/5.4 #masse volumique de l'organe (poumon gauche: 0.550kg/5.4L)
λ = 0.60 #conductivité thermique de l'eau à 298 K (25 °C)
c = 4.1855*10**3 #capacité thermique massique de l'eau, on assimile l'organe à de l'eau
'''

ρ = 0.715 #masse volumique du Chêne pédonculé (matériau de la boîte)
λ = .16 #conductivité thermique du bois de chêne à 298 K (25 °C)
c = 2385 #capacité thermique massique du bois de chêne (source: https://www.thermoconcept-sarl.com/base-de-donnees-chaleur-specifique-ou-capacite-thermique/)

alpha = λ/(ρ*c) #coefficient de diffusivité

r = alpha / (pas_spatial)  # constante utilisée dans le calcul des matrices A et B pour la récurrence

A, B = matrice_AB(r, taille_mat)

T_ext = 35
T_int = 7

########################### D E B U T  D U  P R O G R A M M E #######################

U = init(T_int,T_ext, taille_mat)

for i in range(2): #on calcule U pour t = 1s
    U = calcul_U_t_suivant(U,T_int,taille_mat,E,A,B,λ,N_profondeur,r)


plt.xlabel("Durée (s)")
plt.ylabel("Distance (m)")
plt.title('TEMPERATURE 1D')

plt.imshow(U,extent = [0,L,0,L], aspect = 'auto',cmap = 'afmhot')

cb = plt.colorbar()
cb.set_label("Température (°c)") 

plt.show()
