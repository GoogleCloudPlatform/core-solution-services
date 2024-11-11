// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//
// NOT CURRENTLY USED - this is just example code for a webscraper API
//

package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"os/exec"

	"cloud.google.com/go/firestore"
	"github.com/google/uuid"
	"google.golang.org/api/option"
)

type JobRequest struct {
	Name      string `json:"name"`
	InputData string `json:"input_data"`
}

type JobResponse struct {
	JobID string `json:"job_id"`
}

type BatchJobModel struct {
	ID        string `firestore:"id"`
	Name      string `firestore:"name"`
	InputData string `firestore:"input_data"`
	Type      string `firestore:"type"`
	Status    string `firestore:"status"`
	Message   string `firestore:"message"`
	UUID      string `firestore:"uuid"`
}

const (
	projectID      = "your-gcp-project-id"
	collectionName = "batch_jobs"
)

func main() {
	http.HandleFunc("/start-webscraper", startWebscraperHandler)
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func startWebscraperHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var jobRequest JobRequest
	if err := json.NewDecoder(r.Body).Decode(&jobRequest); err != nil {
		http.Error(w, "Invalid input data", http.StatusBadRequest)
		return
	}

	jobID := uuid.New().String()
	job := BatchJobModel{
		ID:        jobID,
		Name:      jobRequest.Name,
		InputData: jobRequest.InputData,
		Type:      "webscraper",
		Status:    "pending",
		Message:   "Job created",
		UUID:      jobID,
	}

	ctx := context.Background()
	client, err := firestore.NewClient(ctx, projectID, option.WithCredentialsFile("path/to/your/serviceAccountKey.json"))
	if err != nil {
		http.Error(w, "Failed to create Firestore client", http.StatusInternalServerError)
		return
	}
	defer client.Close()

	_, _, err = client.Collection(collectionName).Add(ctx, job)
	if err != nil {
		http.Error(w, "Failed to save job", http.StatusInternalServerError)
		return
	}

	cmd := exec.Command("go", "run", "components/webscraper/main.go")
	cmd.Env = append(os.Environ(), "JOB_ID="+jobID)

	if err := cmd.Start(); err != nil {
		http.Error(w, "Failed to start web scraper", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(JobResponse{JobID: jobID})
}
