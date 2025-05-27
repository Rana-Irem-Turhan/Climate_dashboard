FROM python:3.9

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . /app
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "final_dashboard_with_ui_upgrade:server"]
