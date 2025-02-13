package models

type AuthPayload struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type TokenPayload struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
}
