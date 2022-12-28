FROM golang:1.16

WORKDIR /app

COPY go.mod ./
COPY go.sum ./
COPY main.go ./


RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o helm-to-json.linux
RUN CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 go build -o helm-to-json.macos


ENTRYPOINT [ "/bin/sh" ]
CMD [ "-c", "sleep 3600" ]