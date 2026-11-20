.PHONY: demo run test real

demo:
	python scripts/quickstart.py --demo
real:
	python scripts/download_olist.py
	python scripts/quickstart.py
run:
	streamlit run app/dashboard.py
test:
	pytest -q
