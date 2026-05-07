A streamlit app that runs fluid dynamics simulations thorugh natural language

It uses LLMs to convert a fluid problem described using plain english into fluid dynamics paramaters. LLMs are modular and can use both locally hosted LLMs and via API calls.

The parameters are then comverted to openFOAM templates and simulation is run. After simulation is run, results are displayed and an explaination is givemby the LLM

An example simulation is demonstrated to show the UI and functionality of fluiAI

A simple lid driven cavity problem is the fuild dynamic problem to be solved. It is a standard 2D fluid dynamics benchmark problem involving an incompressible fluid inside a square container with three stationary wall and moving top wall (lid). This involves solving Navier Stokes equation where there is a primary vortex and secondary corner vortices.

<img width="1920" height="1024" alt="Screenshot_2026-05-07_19-47-39" src="https://github.com/user-attachments/assets/76def8aa-9cdf-4e8d-a744-2eb951d59264" />


Future plans involve:
1. LLMs generating the openFOAM templates themselves
2. Integrating Physics Informed Neural Networks (PINNs) as surrogate models for simulation
