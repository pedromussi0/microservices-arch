package config

import (
	"os"
)

type Config struct {
	ServerPort     string
	AuthServiceURL string
	LoggingEnabled bool
}

func Load() (*Config, error) {
	return &Config{
		ServerPort:     os.Getenv("BROKER_PORT"),
		AuthServiceURL: os.Getenv("AUTH_SERVICE_URL"),
		LoggingEnabled: true,
	}, nil
}
