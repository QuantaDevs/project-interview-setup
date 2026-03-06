.PHONY: install install-backend install-frontend run-dev run-frontend-dev run-worker check

###### Installation ######
install i: install-backend install-frontend

install-backend ib:
	@cd backend && uv sync && uv run init_db.py

install-frontend if:
	@cd frontend && npm install --include=dev

###### Services ######
run-dev rd:
	@cd backend && uv run -- flask --debug run -p 8000

run-frontend-dev rfd:
	@cd frontend && npm run dev

run-worker rw:
	@cd backend && nodemon -e py --exec uv run run_worker.py

###### Checks ######
check c:
	@echo "Python version:"
	@python3 --version
	@echo "\nNode version:"
	@node --version
	@echo "\nuv version:"
	@uv --version
	@echo "\ntemporal version:"
	@temporal --version
