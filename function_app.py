import azure.functions as func
import logging
import pandas as pd
import io

app = func.FunctionApp()

@app.blob_output(arg_name="accepted_blob", path="demo/accepted/{name}",
                               connection="stinputfilesblobdemo_STORAGE")
@app.blob_output(arg_name="rejected_blob", path="demo/rejected/{name}",
                               connection="stinputfilesblobdemo_STORAGE")
@app.blob_trigger(arg_name="input_blob", path="demo/inputs/{name}",
                               connection="stinputfilesblobdemo_STORAGE") 
def func_blob(input_blob: func.InputStream, accepted_blob: func.Out[bytes],
               rejected_blob: func.Out[bytes]):
    logging.info(f"Python blob trigger function processed blob\n"
                f"Name: {input_blob.name}\n"
                f"Blob Size: {input_blob.length} bytes")
    
    raw_data = input_blob.read()
    df = pd.read_csv(io.BytesIO(raw_data))

    #check if the locaiton column exists
    if 'Location' in df.columns:
        # any transformation that is required in the correct file will go here
        output_text = df.to_csv(index = False)
        accepted_blob.set(output_text.encode('utf-8'))
    else:
        df['rejected_reason'] = 'Location column does not exist'
        output_text = df.to_csv(index = False)
        rejected_blob.set(output_text.encode('utf-8'))

    logging.info("File written successfully")