package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/pedromussi0/broker-service/internal/models"
	"github.com/pedromussi0/broker-service/internal/services"
)

type Handlers struct {
	brokerService *services.BrokerService
}

func NewHandlers() *Handlers {
	return &Handlers{
		brokerService: services.NewBrokerService(),
	}
}

type Response struct {
	Error   bool   `json:"error"`
	Message string `json:"message"`
	Data    any    `json:"data,omitempty"`
}

func (h *Handlers) HandleSubmission(w http.ResponseWriter, r *http.Request) {
	var requestPayload struct {
		Action       string             `json:"action"`
		Auth         models.AuthPayload `json:"auth,omitempty"`
		RefreshToken string             `json:"refresh_token,omitempty"`
	}

	err := json.NewDecoder(r.Body).Decode(&requestPayload)
	if err != nil {
		h.errorJSON(w, err)
		return
	}

	switch requestPayload.Action {
	case "auth":
		h.authenticate(w, requestPayload.Auth)
	case "refresh":
		h.refreshToken(w, requestPayload.RefreshToken)
	default:
		h.errorJSON(w, fmt.Errorf("unknown action: %s", requestPayload.Action), http.StatusBadRequest)
	}
}

func (h *Handlers) HealthCheck(w http.ResponseWriter, r *http.Request) {
	response := Response{
		Error:   false,
		Message: "Broker service is healthy",
	}
	h.writeJSON(w, http.StatusOK, response)
}

func (h *Handlers) writeJSON(w http.ResponseWriter, status int, data any) error {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	return json.NewEncoder(w).Encode(data)
}

func (h *Handlers) errorJSON(w http.ResponseWriter, err error, status ...int) error {
	statusCode := http.StatusBadRequest
	if len(status) > 0 {
		statusCode = status[0]
	}

	return h.writeJSON(w, statusCode, Response{
		Error:   true,
		Message: err.Error(),
	})
}

func (h *Handlers) authenticate(w http.ResponseWriter, auth models.AuthPayload) {
	authResponse, err := h.brokerService.HandleAuthRequest(auth)
	if err != nil {
		h.errorJSON(w, err, http.StatusUnauthorized)
		return
	}

	response := Response{
		Error:   false,
		Message: "Authenticated successfully",
		Data: map[string]interface{}{
			"access_token":  authResponse.AccessToken,
			"refresh_token": authResponse.RefreshToken,
			"token_type":    authResponse.TokenType,
		},
	}

	h.writeJSON(w, http.StatusOK, response)
}

func (h *Handlers) refreshToken(w http.ResponseWriter, refreshToken string) {
	if refreshToken == "" {
		h.errorJSON(w, fmt.Errorf("refresh token is required"), http.StatusBadRequest)
		return
	}

	authResponse, err := h.brokerService.HandleRefreshToken(refreshToken)
	if err != nil {
		h.errorJSON(w, err, http.StatusUnauthorized)
		return
	}

	response := Response{
		Error:   false,
		Message: "Tokens refreshed successfully",
		Data: map[string]interface{}{
			"access_token":  authResponse.AccessToken,
			"refresh_token": authResponse.RefreshToken,
			"token_type":    authResponse.TokenType,
		},
	}

	h.writeJSON(w, http.StatusOK, response)
}
