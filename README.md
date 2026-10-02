# Thermodynamics Modelling: Bhuj Thermal Performance

A Python-based numerical modelling project investigating transient heat transfer through building walls under a simplified Bhuj summer climate profile.

## Overview

This project uses numerical methods to model how heat moves through different wall materials and how this affects indoor temperature over time.

The initial models compare traditional mud/Bhunga-style construction with modern concrete construction. The project also explores different numerical approaches for solving the one-dimensional heat conduction equation, including:

- Forward Time Central Space (FTCS)
- Backward Time Central Space (BTCS)
- Crank–Nicolson

The models incorporate conduction through the wall and convective heat transfer at the boundaries.

## Current Scope

The current climate input is a **synthetic Bhuj summer temperature profile** based on an idealised daily temperature cycle. It is not currently a direct import of observed or NASA climate data.

The model is intended as an educational numerical experiment rather than a validated building-energy simulation.

## Objectives

The project aims to investigate:

1. How different wall materials affect transient thermal behaviour.
2. How indoor temperature responds to changing outdoor conditions.
3. How numerical methods differ in stability and implementation.
4. How spatial and temporal discretisation affect a numerical heat-transfer model.

## Methods

The simulations use a one-dimensional finite-difference representation of heat conduction.

Material properties such as:

- thermal conductivity
- density
- specific heat capacity

are used to calculate thermal diffusivity.

The project also incorporates simplified convection boundary conditions and a basic room-air energy balance in some models.

## Technologies

- Python
- NumPy
- Matplotlib

## Project Status

This project is currently under development. The repository contains several progressively developed models and numerical experiments.

Future improvements may include more rigorous validation, improved boundary-condition treatment, sensitivity analysis, and the use of real climate datasets.

## Author

**Yash Shivji Halai**

Cambridge International A-Level student interested in mathematics, physics and computation.
