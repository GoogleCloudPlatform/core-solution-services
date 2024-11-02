FROM golang:1.20-alpine

WORKDIR /app

# Install git for private dependencies if needed
RUN apk add --no-cache git

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN go build -o webscraper ./main.go

# Run the web service on container startup
CMD ["/app/webscraper"]
