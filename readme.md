## Environment Versions

- **Python**: 3.11.7
- **OpenJDK**: 11.0.25 (2024-10-15)
    - OpenJDK Runtime Environment Homebrew (build 11.0.25+0)
    - OpenJDK 64-Bit Server VM Homebrew (build 11.0.25+0, mixed mode)

## Setup Instructions

1. Install dependencies:
     ```sh
     pip install --no-cache-dir -r requirements.txt
     ```

2. Run the `scrape.py` script to fetch comments and save them to `play_store.csv` and `app_store.csv`.

3. Copy the `morphology.proto` script from [here](https://github.com/ahmetaa/zemberek-nlp/blob/master/grpc/src/main/proto/morphology.proto) to a directory and run:
     ```sh
     python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. morphology.proto
     ```
     After running the command, copy the generated `morphology_pb2.py` and `morphology_pb2_grpc.py` scripts to the project directory.

4. Download the `zemberek-full.jar` file from [this link](https://drive.google.com/file/d/1RRuFK43JqcHcthB3fV2IEpPftWoeoHAu/view?usp=drive_link) and start the Zemberek gRPC server with:
     ```sh
     java -jar zemberek-full.jar StartGrpcServer
     ```

5. Run the `clean.py` script to filter comments and lemmatize them using Zemberek.

6. Run the `lda.py` script to train the model.