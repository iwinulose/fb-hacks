package main

import "fmt"
import "log"
import "flag"
import "os"
import "io"
import "io/ioutil"
import "bufio"
import "bytes"
import "net/url"
import "net/http"
import "encoding/json"

type User struct {
	Name string
	Id int
}


type Message struct {
	Id string
	Timestamp int 
	User User
	Text string
}

const DEFAULT_TOKEN_PATH = "token"
const DEFAULT_THREADID_PATH = "id"

func init() {
	log.SetFlags(0)
}

func readFirstLine(path string) (string, error) {
	var line []byte
	var isPrefix bool
	var err error
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()
	reader := bufio.NewReader(file)
	slices := make([][]byte, 0)
	isPrefix = true
	for isPrefix {
		line, isPrefix, err = reader.ReadLine()
		if err != nil {
			break;
		}
		slices = append(slices, line)
	}
	lineBytes := bytes.Join(slices, nil)
	return string(lineBytes), err
}

func makeURL(token, id string) string {
	params := url.Values{}
	params.Add("access_token", token)
	params.Add("date_format", "U")
	paramString := params.Encode()
	url := fmt.Sprintf("https://graph.facebook.com/%s/comments?%s", id, paramString)
	return url
}

func ParseUser(json map[string]interface{}) User {
	u := User{}
	u.Name = json["name"].(string)
	u.Id = int(json["id"].(float64))
	return u
}

func ParseMessage(json map[string]interface{}) Message {
	m := Message{}
	m.Id = json["id"].(string)
	m.Timestamp = int(json["created_time"].(float64))
	m.User = ParseUser(json["from"].(map[string]interface{}))
	m.Text = json["message"].(string)
	return m
}

func parseMessages(body io.ReadCloser) ([]Message, error) {
	defer body.Close()
	var dest map[string]interface{}
	messages := make([]Message, 0, 25)
	bytes, _ := ioutil.ReadAll(body)
	json.Unmarshal(bytes, &dest)
	messageMaps := dest["data"].([]interface{})
	for _, v := range messageMaps {
		messages = append(messages, ParseMessage(v.(map[string]interface{})))
	}
	return nil, nil
}

func fetchMessages(url string, numMessages uint) ([]Message, error) {
	messages := make([]Message, 0, numMessages)
	response, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	parsed, err := parseMessages(response.Body)
	messages = append(messages, parsed...)
	return messages, err
}

func main() {
	var tokenPath string
	var idPath string
	flag.StringVar(&tokenPath, "token", DEFAULT_TOKEN_PATH, "Path to a file containing the Facebook access token on the first line.")
	flag.StringVar(&idPath, "id", DEFAULT_THREADID_PATH, "Path to a file containing the thread ID on the first line.")
	flag.Parse()
	token, err := readFirstLine(tokenPath)
	if err != nil {
		log.Fatal("Could not read token:", err)
	}
	id, err := readFirstLine(idPath)
	if err != nil {
		log.Fatalln("Could not read id:", err)
	}
	url := makeURL(token, id)
	messages, err := fetchMessages(url, 5)
	fmt.Println(messages)
}
