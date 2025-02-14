package models

import (
	"github.com/pedromussi0/broker-service/internal/pkg/types"
)

type AuthPayload struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type UserPayload struct {
	Email       string         `json:"email"`
	Password    string         `json:"password"`
	FullName    *string        `json:"full_name,omitempty"`
	IsActive    bool           `json:"is_active,omitempty"`
	IsSuperUser bool           `json:"is_superuser,omitempty"`
	Id          int            `json:"id,omitempty"`
	CreatedAt   types.JSONTime `json:"created_at"`
	UpdatedAt   types.JSONTime `json:"updated_at"`
}

type TokenPayload struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
}
