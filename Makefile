.PHONY: help setup start stop clean deploy-k8s chaos-test dashboard

help:
	@echo "KRAKEN - Self-Healing Intelligence Core"
	@echo ""
	@echo "Commands:"
	@echo "  setup       - Initialize the project"
	@echo "  start       - Start all services"
	@echo "  stop        - Stop all services"
	@echo "  deploy-k8s  - Deploy to Kubernetes"
	@echo "  chaos-test  - Run chaos engineering tests"
	@echo "  dashboard   - Open the dashboard"
	@echo "  logs        - View AI Brain logs"
	@echo "  clean       - Clean up all containers"

setup:
	@echo "Setting up KRAKEN..."
	mkdir -p logs
	mkdir -p data
	@echo "✅ Setup complete"

start:
	@echo "Starting KRAKEN..."
	docker-compose up -d
	@echo "✅ KRAKEN is now running"
	@echo "📊 Dashboard: http://localhost:3000"
	@echo "🤖 AI Brain: http://localhost:8000/docs"
	@echo "📈 Prometheus: http://localhost:9090"

stop:
	docker-compose down

deploy-k8s:
	@echo "Deploying to Kubernetes..."
	kubectl apply -f kubernetes/namespace.yaml
	kubectl apply -f kubernetes/microservices/
	kubectl apply -f kubernetes/monitoring/
	@echo "✅ Kubernetes deployment complete"

chaos-test:
	@echo "Running chaos tests..."
	curl -X POST http://localhost:8000/chaos-response \
		-H "Content-Type: application/json" \
		-d '{"type":"service_failure","service":"user-service"}'
	@echo "✅ Chaos test complete"

dashboard:
	@echo "Opening dashboard..."
	open http://localhost:3000 || xdg-open http://localhost:3000 || start http://localhost:3000

logs:
	docker-compose logs -f ai-brain

clean:
	docker-compose down -v
	rm -rf logs/*
	@echo "✅ Cleanup complete"