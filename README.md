# AggieAI — Intelligent Course & GE Recommender

AggieAI is an AI-powered course recommendation and academic planning tool designed for UC Davis students.

The platform combines **Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), semantic search, and recommendation systems** to help students discover courses that match their academic requirements, interests, and preferences.

Instead of manually searching through the UC Davis course catalog, students can describe what they are looking for in natural language and receive personalized course recommendations with explanations.

---

## Problem

Choosing classes can be difficult because students often need to consider several factors at once:

- Remaining General Education requirements
- Major or prerequisite requirements
- Number of units
- Course topics and personal interests
- Previously completed courses
- AP/IB or transfer credit
- Course prerequisites
- Academic workload and preferences

Course information is available across university resources, but finding and comparing relevant courses manually can be time-consuming.

AggieAI aims to make this process easier by providing a single intelligent interface for course discovery and recommendation.

---

## Example

A student could ask:

> "I still need Arts & Humanities GE credit. I like psychology, movies, AI, and business, and I want a 4-unit class without many prerequisites."

AggieAI could return:

### Recommended Courses

**1. Course A — 94% Match**

Why it was recommended:

- Satisfies the student's remaining GE requirement
- Course description is highly related to the student's interests
- Fits the desired unit count
- Has few or no prerequisites

**2. Course B — 89% Match**

Why it was recommended:

- Matches interests in psychology and technology
- Satisfies an applicable GE category
- Fits the student's academic plan

Students can then ask follow-up questions such as:

> "Why did you recommend Course A?"

> "Which of these classes has the fewest prerequisites?"

> "Can I take this course if I haven't taken Course X?"

> "Show me classes related to AI that also satisfy one of my remaining GEs."

---

# Core Features

## 1. Personalized Course Recommendations

Students enter information such as:

- Completed courses
- Remaining GE requirements
- Major
- Academic interests
- Preferred number of units
- Topics they want to explore
- Courses they want to avoid

AggieAI ranks courses based on how well they match the student's needs.

---

## 2. Natural-Language Course Search

Students do not need to know specific course codes or catalog terminology.

Example queries:

> "Find me an interesting GE related to technology."

> "I like film and psychology. What classes might I enjoy?"

> "What 4-unit classes can satisfy my remaining Arts & Humanities requirement?"

An LLM interprets the student's request and converts it into structured search and recommendation criteria.

---

## 3. Semantic Course Matching

AggieAI uses **text embeddings** to understand the meaning of course descriptions.

Instead of relying only on keywords, the system compares a student's interests with the semantic meaning of course descriptions.

For example:

```text
Student Interests
        ↓
"AI, psychology, human behavior"
        ↓
Embedding Model
        ↓
Student Interest Vector
        ↓
Similarity Search
        ↓
Relevant Course Embeddings
```

This allows the system to discover relevant courses even when the student's exact keywords do not appear in the course description.

---

## 4. Intelligent Recommendation Ranking

Courses are ranked using multiple factors.

An example recommendation score could be:

```text
Recommendation Score =

40% Interest Similarity
25% GE Requirement Match
15% Unit Preference
10% Prerequisite Compatibility
10% Additional Student Preferences
```

The ranking formula can be adjusted as the project develops.

Potential future factors could include:

- Course difficulty
- Professor ratings
- Schedule compatibility
- Historical enrollment
- Major relevance
- Career relevance
- Student feedback

---

## 5. Course Information RAG System

AggieAI uses **Retrieval-Augmented Generation (RAG)** to answer questions about courses using official academic information.

Instead of asking an LLM to answer entirely from its pretrained knowledge, relevant course information is retrieved first.

```text
Student Question
        ↓
Embedding
        ↓
Vector Search
        ↓
Relevant Course / Catalog Information
        ↓
LLM
        ↓
Grounded Answer
```

Possible information sources include:

- UC Davis course catalog
- Course descriptions
- Prerequisites
- GE classifications
- Unit information
- AP/IB credit policies
- Transfer credit information

Whenever possible, answers should reference the original source used by the system.

---

## 6. Prerequisite Checking

Students can ask questions such as:

> "Can I take ECS XXX?"

> "What classes am I missing before taking this course?"

> "What classes require ECS XXX?"

AggieAI can analyze prerequisite relationships and determine whether a student has completed the necessary coursework.

A future version could represent prerequisites as a graph.

```text
Course A
   ↓
Course B
   ↓
Course C
   ↓
Advanced Course
```

This could allow the system to generate prerequisite paths automatically.

---

# System Architecture

A possible architecture for AggieAI:

```text
                     Student
                        │
                        ▼
               ┌─────────────────┐
               │   Web Interface │
               └────────┬────────┘
                        │
                        ▼
               Natural Language Query
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       Recommendation         RAG System
           Engine                 │
              │              Vector Search
              │                   │
       Course Ranking       Course Catalog
              │                   │
              └─────────┬─────────┘
                        ▼
                       LLM
                        │
                        ▼
             Personalized Response
```

---

# AI / ML Components

AggieAI provides opportunities to experiment with several machine learning and GenAI concepts.

### Large Language Models

Used for:

- Understanding user queries
- Extracting student preferences
- Answering course questions
- Generating recommendation explanations

### Retrieval-Augmented Generation

Used to ground LLM responses in official course information.

### Embeddings

Used to represent:

- Course descriptions
- Student interests
- Academic topics

as numerical vectors.

### Vector Search

Used to find courses semantically similar to the student's interests.

Possible technologies include:

- FAISS
- ChromaDB
- Pinecone
- PostgreSQL + pgvector

### Recommendation Systems

Initial versions can use **content-based filtering**.

Future versions could explore:

- Collaborative filtering
- Hybrid recommendation systems
- Learning-to-rank models
- User feedback loops

---

# Potential Tech Stack

## Frontend

- React
- Next.js
- TypeScript
- Tailwind CSS

## Backend

- Python
- FastAPI
- REST APIs

## AI / ML

- Python
- Sentence Transformers
- OpenAI / other LLM APIs
- scikit-learn
- NumPy
- Pandas

## Vector Database

Possible options:

- FAISS
- ChromaDB
- Pinecone
- pgvector

## Database

- PostgreSQL
- Supabase

## Deployment

Possible options:

- Vercel
- Render
- Railway
- AWS

---

# Possible Data Structure

Each course could be stored using a structure similar to:

```json
{
  "course_code": "ECS XXX",
  "title": "Example Course",
  "description": "Course description...",
  "units": 4,
  "prerequisites": [
    "ECS XXX"
  ],
  "ge_categories": [
    "Science and Engineering"
  ],
  "department": "Computer Science"
}
```

A corresponding course embedding could also be stored in the vector database.

---

# Recommendation Pipeline

A simplified recommendation pipeline could look like:

```text
Student Profile
      │
      ├── Completed Courses
      ├── Remaining GE Requirements
      ├── Interests
      ├── Unit Preferences
      └── Other Preferences
              │
              ▼
      Filter Eligible Courses
              │
              ▼
     Generate Interest Embedding
              │
              ▼
      Semantic Similarity Search
              │
              ▼
     Calculate Ranking Scores
              │
              ▼
        Top-K Courses
              │
              ▼
      LLM Explanations
```

---

# MVP

The first version of AggieAI should remain relatively small.

The MVP could support:

1. UC Davis course dataset
2. Course descriptions
3. Units
4. GE categories
5. Course prerequisites
6. User interest input
7. Semantic course search
8. Personalized course ranking
9. Natural-language questions
10. Explanations for recommendations

Example MVP interaction:

```text
User:

I need an Arts & Humanities GE.
I like film, technology, psychology, and music.
I want a 4-unit course.

AggieAI:

Based on your interests and remaining GE requirements,
here are five courses that may be a good fit:

1. Course A — 94% Match
2. Course B — 91% Match
3. Course C — 86% Match
4. Course D — 82% Match
5. Course E — 79% Match
```

---

# Stretch Goals

Once the MVP works, additional features could include:

### Schedule-Aware Recommendations

Recommend courses that fit around the student's existing schedule.

### Professor Information

Incorporate instructor information when available.

### Degree Progress Tracking

Allow students to enter completed coursework and visualize their remaining degree requirements.

### AP / IB Credit Support

Allow students to enter AP or IB scores and automatically identify applicable course credit.

### Transfer Credit Support

Help transfer students understand how previous coursework applies to UC Davis requirements.

### Career-Based Recommendations

Students could enter a career goal such as:

> "I want to become an ML engineer."

AggieAI could recommend courses related to the skills needed for that career.

### Conversational Academic Planning

Students could ask:

> "What should I take next quarter?"

AggieAI could combine prerequisites, GE requirements, interests, and course availability to generate a suggested schedule.

### Feedback-Based Recommendations

Students could like or dislike recommendations.

```text
Course A 👍
Course B 👎
Course C 👍
```

The recommendation system could gradually learn the student's preferences.

---

# Suggested Team Structure

The project can be divided into several areas.

### Data / RAG Team

Responsibilities:

- Collect course information
- Clean and structure the dataset
- Build document chunking pipelines
- Generate embeddings
- Implement vector search

### Recommendation / ML Team

Responsibilities:

- Design recommendation scoring
- Implement semantic similarity
- Develop ranking algorithms
- Evaluate recommendation quality

### Backend / LLM Team

Responsibilities:

- Build FastAPI endpoints
- Connect LLM services
- Implement RAG
- Handle user queries
- Generate recommendation explanations

### Frontend Team

Responsibilities:

- Build the student interface
- Display course recommendations
- Build preference forms
- Build conversational search
- Display recommendation explanations

---

# Suggested Development Phases

## Phase 1 — Data

- Collect UC Davis course information
- Define the course schema
- Clean and normalize course data
- Store courses in a database

## Phase 2 — Semantic Search

- Generate course embeddings
- Store embeddings
- Implement semantic similarity search

## Phase 3 — Recommendation Engine

- Create student preference profiles
- Implement filtering
- Create recommendation scoring
- Return ranked courses

## Phase 4 — RAG

- Build document retrieval
- Connect an LLM
- Generate grounded answers
- Add source references

## Phase 5 — Frontend

- Create search interface
- Create student preference form
- Display recommendations
- Add conversational interaction

## Phase 6 — Evaluation

Evaluate:

- Recommendation relevance
- Retrieval accuracy
- Hallucination rate
- Response quality
- User satisfaction

---

# Project Goals

By completing AggieAI, the team will gain hands-on experience with:

- Large Language Models
- Retrieval-Augmented Generation
- Embeddings
- Vector databases
- Semantic search
- Recommendation systems
- Ranking algorithms
- API development
- Full-stack AI applications
- AI evaluation
- Prompt engineering

Most importantly, the project focuses these technologies on a real problem faced by UC Davis students.

---

# Disclaimer

AggieAI is intended as an experimental student project and academic planning assistant.

It should **not replace official academic advising**.

Students should verify degree requirements, prerequisites, GE requirements, and course information using official UC Davis resources or an academic advisor before making enrollment decisions.

---

1. What Should the Final Product Do?
By the end of Week 6, a student should be able to:
1. Open the AggieAI website.
2. Enter their academic interests, such as AI, psychology, music, or business.
3. Select remaining GE requirements.
4. Specify preferred units and optionally completed courses.
5. Ask natural-language questions about courses.
6. Receive five personalized course recommendations.
7. See explanations for why each course was recommended.
8. View course details, including units, GE categories, and prerequisites.
9. Ask follow-up questions about recommended courses.

---
# Contributors

MLSN Project Team

**Project Lead:** TBD

**Developers:** TBD

---

# License

License information will be added as the project develops.
