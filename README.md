# Peanut
a simple web-ui client for llama.cpp


HOW TO USE

Download llama.cpp and run at port 30000:

    ./llama-server -m [LLM_MODEL] --port 30000

then streamlit run it at 8080:

    ./streamlit run peanut.py --server.port 8080

Change ports at will.



FEATURES

For modal dialog window I am using "streamlit-modal" package found at: https://github.com/teamtv/streamlit_modal

I didn't want to use the defualt 'X' close button so commented out that part of the code.

Other than that a full credit goes to the original author who's done an awesome job. Thanks!

Icons for logo, user, and assistant can be replaced with PNG image in /asset folder.

Basic support for Chat History and System Prompt save/load is included.
Both of them are saved and loaded as plain TXT files.




Thanks!

Steve

sojhung@gmail.com

~                               
