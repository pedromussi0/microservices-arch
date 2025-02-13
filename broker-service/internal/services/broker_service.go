package services

import (
	"bytes"
	"encoding/json"
	"net/http"

	"github.com/pedromussi0/broker-service/internal/config"
	"github.com/pedromussi0/broker-service/internal/models"
)

type BrokerService struct {
	client *http.Client
	config *config.Config
}

func NewBrokerService() *BrokerService {
	cfg, _ := config.Load()
	return &BrokerService{
		client: &http.Client{},
		config: cfg,
	}
}

func (s *BrokerService) HandleAuthRequest(auth models.AuthPayload) error {
	jsonData, err := json.Marshal(auth)
	if err != nil {
		return err
	}

	request, err := http.NewRequest(
		"POST",
		s.config.AuthServiceURL+"/token",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return err
	}

	request.Header.Set("Content-Type", "application/json")

	_, err = s.client.Do(request)
	if err != nil {
		return err
	}

	return nil
}
