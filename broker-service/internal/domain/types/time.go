package types

import (
	"strings"
	"time"
)

type JSONTime time.Time

func (t *JSONTime) UnmarshalJSON(b []byte) error {
	s := strings.Trim(string(b), "\"")
	if s == "null" || s == "" {
		return nil
	}

	// Parse timestamp without timezone, then set to UTC
	parsedTime, err := time.Parse("2006-01-02T15:04:05.999999", s)
	if err != nil {
		return err
	}

	*t = JSONTime(parsedTime.UTC())
	return nil
}

func (t JSONTime) MarshalJSON() ([]byte, error) {
	return []byte(`"` + time.Time(t).Format("2006-01-02T15:04:05.999999") + `"`), nil
}

func (t JSONTime) Time() time.Time {
	return time.Time(t)
}
