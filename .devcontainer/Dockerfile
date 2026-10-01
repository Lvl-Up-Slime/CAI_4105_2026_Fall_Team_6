FROM docker.io/library/python:3.11-slim

RUN pip install --no-cache-dir \
    jupyterlab \
    pandas \
    numpy \
    statsmodels \
    scikit-learn \
    matplotlib \
    xgboost \
    ucimlrepo

WORKDIR /app
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
