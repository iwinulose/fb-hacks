package main

import "fmt"
import "flag"
import "os"
import "bufio"
//import "net/url"
//import "net/http"

type User struct {
	Name string
	Id int
}

type Message struct {
	Timestamp int 
	Id int
	User *User
	Text string
}

const DEFAULT_TOKEN_PATH = "token"
const DEFAULT_THREADID_PATH = "id"

func readFirstLine(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()
	reader := bufio.NewReader(file)
	return reader.ReadString('\n')
}

func main() {
	var tokenPath string
	var idPath string
	flag.StringVar(&tokenPath, "token", DEFAULT_TOKEN_PATH, "Path to a file containing the Facebook access token on the first line.")
	flag.StringVar(&idPath, "id", DEFAULT_THREADID_PATH, "Path to a file containing the thread ID on the first line.")
	flag.Parse()
	token, _ := readFirstLine(tokenPath)
	id, _ := readFirstLine(idPath)
	fmt.Printf("token %s id %s\n", token, id)
}
