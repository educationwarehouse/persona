

def _setup_initial_config_file():
    import os
    print('testing for existence of the appconfig file')
    # compose the filepath of the targeted config file 
    app_config_file = os.path.join(request.folder,'private','appconfig.ini')

    if not os.path.exists(app_config_file):
        # if it isn't there, copy the sample 
        import shutil
        sample_file = os.path.join(request.folder,'private','appconfig.example.ini')
        print('copying the example config file to this installation specific file')
        shutil.copy(sample_file, app_config_file)


# execute this call every invocation of the server and cache it's result to run only once. 
cache.ram('_setup_initial_config_file',_setup_initial_config_file)

