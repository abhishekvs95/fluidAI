A streamlit app that runs fluid dynamics simulations thorugh natural language

It uses LLMs to convert a fluid problem described using plain english into fluid dynamics paramaters. LLMs are modular and can use both locally hosted LLMs and via API calls.

The parameters are then comverted to openFOAM templates and simulation is run. After simulation is run, results are displayed and an explaination is givemby the LLM

An example simulation is demonstrated to show the UI and functionality of fluiAI

A simple lid driven cavity problem is the fuild dynamic problem to be solved. It is a standard 2D fluid dynamics benchmark problem involving an incompressible fluid inside a square container with three stationary wall and moving top wall (lid). This involves solving Navier Stokes equation where there is a primary vortex and secondary corner vortices.

<img width="1920" height="1024" alt="Screenshot_2026-05-07_19-47-39" src="https://github.com/user-attachments/assets/76def8aa-9cdf-4e8d-a744-2eb951d59264" />
<img width="1920" height="1024" alt="Screenshot_2026-05-07_19-48-16" src="https://github.com/user-attachments/assets/ae717932-b4bd-4de9-9216-9c34485dd7c9" />
<img width="1920" height="1024" alt="Screenshot_2026-05-07_19-48-07" src="https://github.com/user-attachments/assets/35cabd8d-f751-4c16-b196-ba5d0cb214b2" />
<img width="1920" height="1024" alt="Screenshot_2026-05-07_19-48-25" src="https://github.com/user-attachments/assets/a9fc62ec-4d31-4c8f-8edd-4f639108fe54" />
<img width="1920" height="1024" alt="Screenshot_2026-05-07_19-49-08" src="https://github.com/user-attachments/assets/610a5aa2-f8db-4a63-b507-e5247df001ca" />


Future plans involve:
1. LLMs generating the openFOAM templates themselves
2. Integrating Physics Informed Neural Networks (PINNs) as surrogate models for simulation
