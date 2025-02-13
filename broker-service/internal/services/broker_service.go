package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/pedromussi0/broker-service/internal/config"
	"github.com/pedromussi0/broker-service/internal/models"
)

type BrokerService struct {
	client *http.Client
	config *config.Config
}

type AuthResponse struct {
	AccessToken  string `json:"access_token,omitempty"`
	RefreshToken string `json:"refresh_token,omitempty"`
	TokenType    string `json:"token_type,omitempty"`
	Valid        bool   `json:"valid,omitempty"`
	Error        string `json:"detail,omitempty"`
}

func NewBrokerService() *BrokerService {
	cfg, _ := config.Load()
	return &BrokerService{
		client: &http.Client{},
		config: cfg,
	}
}

func (s *BrokerService) HandleAuthRequest(auth models.AuthPayload) (*AuthResponse, error) {
	jsonData, err := json.Marshal(auth)
	if err != nil {
		return nil, fmt.Errorf("error marshaling auth payload: %w", err)
	}

	request, err := http.NewRequest(
		"POST",
		s.config.AuthServiceURL+"/token",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	request.Header.Set("Content-Type", "application/json")

	response, err := s.client.Do(request)
	if err != nil {
		return nil, fmt.Errorf("error making request to auth service: %w", err)
	}
	defer response.Body.Close()

	body, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	var authResponse AuthResponse
	if err := json.Unmarshal(body, &authResponse); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %w", err)
	}

	if response.StatusCode != http.StatusOK {
		if authResponse.Error != "" {
			return &authResponse, fmt.Errorf("authentication failed: %s", authResponse.Error)
		}
		return &authResponse, fmt.Errorf("authentication failed with status code: %d", response.StatusCode)
	}

	return &authResponse, nil
}
