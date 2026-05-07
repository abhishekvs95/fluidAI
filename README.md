A streamlit app that runs fluid dynamics simulations thorugh natural language

It uses LLMs to convert a fluid problem described using plain english into fluid dynamics paramaters. LLMs are modular and can use both locally hosted LLMs and via API calls.

The parameters are then comverted to openFOAM templates and simulation is run. After simulation is run, results are displayed and an explaination is givemby the LLM

Future plans involve:
1. LLMs generating the openFOAM templates themselves
2. Integrating Physics Informed Neural Networks (PINNs) as surrogate models for simulation
