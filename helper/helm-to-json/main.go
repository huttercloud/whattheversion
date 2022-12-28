package main

import (
	"fmt"
	"github.com/ghodss/yaml"
	"io"
	"net/http"
	"os"
)

func main() {

	url := os.Args[1]

	resp, err := http.Get(url)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	// read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}

	json, err := yaml.YAMLToJSON(body)
	if err != nil {
		panic(err)
	}
	fmt.Println(string(json))
}
