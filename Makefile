lidarts-build:
	docker build -t lidarts:latest .

lidarts-build-nocache:
	docker build --no-cache -t lidarst:latest .


lidarts-run: 
	docker run -h lidarst --name lidarts -p 5000:5000 -d lidarts:latest


lidarts-destroy:
	docker stop lidarts && docker rm lidarts

