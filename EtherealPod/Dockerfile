FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum* ./
RUN go mod download

COPY main.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o controller .

FROM alpine:latest
RUN apk --no-cache add ca-certificates

# Put the binary at an absolute path
COPY --from=builder /app/controller /controller

# Run it as the container entrypoint (so k8s args work)
ENTRYPOINT ["/controller"]
