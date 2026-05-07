# FluidAI - Solve CFD Problems Using Natural Language

A streamlit app that runs fluid dynamics simulations through natural language. It uses LLMs to convert a fluid problem described using plain english into fluid dynamics paramaters. LLMs are modular and can use both locally hosted LLMs and via API calls. The parameters are then comverted to openFOAM templates and simulation is run. After simulation is run, results are displayed and an explaination is givemby the LLM

### CFD demo - Lid Driven Cavity Problem

An example simulation is demonstrated to show the UI and functionality of fluiAI. A simple lid driven cavity problem is the fuild dynamic problem to be solved. It is a standard 2D fluid dynamics benchmark problem involving an incompressible fluid inside a square container with three stationary wall and moving top wall (lid). This involves solving Navier Stokes equation where there is a primary vortex and secondary corner vortices.

Below is the streamlit interface showing text input and the parameters are chosen by the LLM of choice as input for simulation
<img width="1864" height="935" alt="ss1" src="https://github.com/user-attachments/assets/8a86b3fe-5844-4add-982c-17c1fcb84ce5" />

After simulation is done, the results can be viwed as the velocity field and residuals
<img width="1857" height="929" alt="ss2" src="https://github.com/user-attachments/assets/3bb3677c-151e-4eec-a011-6dda806a6d63" />

This image shows the primary vortex at the middle and secondary corner vortex at the top right corner after 10 seconds of running the simulation.
<img width="1864" height="935" alt="ss3" src="https://github.com/user-attachments/assets/5473f254-9d2a-4575-ae95-3278162ddda2" />

This shows the residuals which basically shows how much error is remaining based on the governing equation (here, Navier Stokes is used)
<img width="1861" height="935" alt="ss4" src="https://github.com/user-attachments/assets/b65949e0-dfe5-4bc9-8d7e-58d3db48243b" />

The logs from the CFD solver, openFOAM can be viewed here
<img width="1864" height="932" alt="ss5" src="https://github.com/user-attachments/assets/d8f16f75-bced-42de-a7e2-bca5222480a5" />




### Future plans
1. LLMs generating the openFOAM templates themselves
2. Integrating Physics Informed Neural Networks (PINNs) as surrogate models for simulation
