package config

type Config struct {
	ServerPort     string
	AuthServiceURL string
	LoggingEnabled bool
}

func Load() (*Config, error) {
	// In a real application, you might load this from environment variables
	// or a configuration file
	return &Config{
		ServerPort:     "8080",
		AuthServiceURL: "http://authentication-service:8000",
		LoggingEnabled: true,
	}, nil
}
