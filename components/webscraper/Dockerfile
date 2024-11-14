FROM golang:1.23.2-alpine

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

ENTRYPOINT ["/app/webscraper"]
