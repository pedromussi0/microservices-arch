package services

import (
	"bytes"
	"fmt"
	"io"
	"net/http"

	jsoniter "github.com/json-iterator/go"
	"github.com/pedromussi0/broker-service/internal/config"
	"github.com/pedromussi0/broker-service/internal/models"
)

type BrokerService struct {
	client *http.Client
	config *config.Config
}

type AuthResponse struct {
	models.TokenPayload
	Valid bool   `json:"valid,omitempty"`
	Error string `json:"detail,omitempty"`
}

type UserResponse struct {
	models.UserPayload
	Valid bool        `json:"valid,omitempty"`
	Error interface{} `json:"detail,omitempty"`
}

type RefreshTokenRequest struct {
	RefreshToken string `json:"refresh_token"`
}

func NewBrokerService() *BrokerService {
	cfg, _ := config.Load()
	return &BrokerService{
		client: &http.Client{},
		config: cfg,
	}
}

func (s *BrokerService) HandleAuthRequest(auth models.AuthPayload) (*AuthResponse, error) {
	jsonData, err := jsoniter.Marshal(auth)
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
	if err := jsoniter.Unmarshal(body, &authResponse); err != nil {
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

func (s *BrokerService) HandleRefreshToken(refreshToken string) (*AuthResponse, error) {
	tokenRequest := RefreshTokenRequest{
		RefreshToken: refreshToken,
	}

	jsonData, err := jsoniter.Marshal(tokenRequest)
	if err != nil {
		return nil, fmt.Errorf("error marshaling refresh token request: %w", err)
	}

	request, err := http.NewRequest(
		"POST",
		s.config.AuthServiceURL+"/refresh-token",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, fmt.Errorf("error creating refresh token request: %w", err)
	}

	request.Header.Set("Content-Type", "application/json")

	response, err := s.client.Do(request)
	if err != nil {
		return nil, fmt.Errorf("error making refresh token request: %w", err)
	}
	defer response.Body.Close()

	body, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading refresh token response: %w", err)
	}

	var authResponse AuthResponse
	if err := jsoniter.Unmarshal(body, &authResponse); err != nil {
		return nil, fmt.Errorf("error unmarshaling refresh token response: %w", err)
	}

	if response.StatusCode != http.StatusOK {
		if authResponse.Error != "" {
			return &authResponse, fmt.Errorf("token refresh failed: %s", authResponse.Error)
		}
		return &authResponse, fmt.Errorf("token refresh failed with status code: %d", response.StatusCode)
	}

	return &authResponse, nil
}

func (s *BrokerService) HandleRegisterRequest(user models.UserPayload) (*UserResponse, error) {
	jsonData, err := jsoniter.Marshal(user)
	if err != nil {
		return nil, fmt.Errorf("error marshaling user payload: %w", err)
	}

	request, err := http.NewRequest(
		"POST",
		s.config.AuthServiceURL+"/register",
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

	var userResponse UserResponse
	if err := jsoniter.Unmarshal(body, &userResponse); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %w", err)
	}

	if response.StatusCode != http.StatusCreated {
		if userResponse.Error != "" {
			return &userResponse, fmt.Errorf("registration failed: %s", userResponse.Error)
		}
		return &userResponse, fmt.Errorf("registration failed with status code: %d", response.StatusCode)
	}

	return &userResponse, nil
}
