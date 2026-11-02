import random

QUESTIONS_BANK = {
    "Software Developer": [
        "Explain the difference between a list and a tuple in Python.",
        "How do you handle exceptions in Python and what is the purpose of finally?",
        "What is REST API and what are the main HTTP methods used?",
        "Describe the MVC architecture and the responsibility of each layer.",
        "How would you optimize a slow SQL query with indexes?",
        "Explain the difference between process and thread, and how concurrency is handled in modern runtimes.",
        "What is the difference between synchronous and asynchronous programming in web backends?",
        "How does Garbage Collection work in managed languages like Python or Java?",
        "Explain the SOLID principles of object-oriented design with concrete examples.",
        "What are database transactions and what does ACID compliance guarantee?",
        "Explain how hashing works in a Hash Map and how collisions are resolved.",
        "What is the difference between SQL and NoSQL databases, and when would you choose one over the other?",
        "How do you implement authentication and authorization using JWTs in REST APIs?",
        "What is Git rebase versus Git merge, and in what situations would you use each?",
        "Explain how caching strategies like Redis or Memcached can reduce database load.",
        "What are microservices, and what are their primary advantages and trade-offs compared to monoliths?",
        "How do you handle rate limiting and API throttling in public-facing services?",
        "Explain the difference between TCP and UDP, and give examples where each is preferred.",
        "What is database normalization and why is 3NF commonly targeted in relational schemas?",
        "How do you approach writing comprehensive unit, integration, and end-to-end tests?",
        "Explain the concept of race conditions and how mutexes or locks prevent them.",
        "What is continuous integration and continuous deployment (CI/CD), and why is it essential?",
        "How do you prevent common web vulnerabilities like SQL Injection, XSS, and CSRF?",
        "Explain how Docker containerization differs from running applications in virtual machines.",
        "What is event-driven architecture and how do message brokers like Kafka or RabbitMQ work?",
        "How do you design a database schema to support pagination efficiently for large datasets?",
        "Explain the difference between depth-first search (DFS) and breadth-first search (BFS).",
        "What is the role of an API Gateway and reverse proxy in modern distributed systems?",
        "How do you monitor application performance, track error rates, and handle production logging?",
        "Describe the trade-offs between horizontal and vertical scaling in server infrastructure."
    ],
    "Data Scientist": [
        "Explain what overfitting is and how you would prevent it.",
        "What is the difference between supervised and unsupervised learning?",
        "How do you handle missing values in a dataset during preprocessing?",
        "Explain the concept of p-value and statistical significance.",
        "What are the pros and cons of Decision Trees vs Random Forests?",
        "Explain the bias-variance tradeoff and its impact on model generalization.",
        "How does cross-validation help in assessing model performance and tuning hyperparameters?",
        "What is the difference between L1 (Lasso) and L2 (Ridge) regularization?",
        "Explain how ROC curves and AUC metrics are used to evaluate binary classification models.",
        "What is feature engineering, and can you share an example of creating high-value derived features?",
        "Explain the mathematical intuition behind Logistic Regression and the sigmoid activation function.",
        "How do you detect and mitigate multicollinearity among independent variables in regression?",
        "What is data leakage in machine learning pipelines and how do you strictly avoid it?",
        "How do Gradient Boosting algorithms like XGBoost or LightGBM differ from Random Forests?",
        "Explain the K-Means clustering algorithm and how you determine the optimal number of clusters (K).",
        "What is Principal Component Analysis (PCA) and how does it achieve dimensionality reduction?",
        "How do you handle highly imbalanced datasets when training classification models?",
        "Explain the difference between precision, recall, and F1-score in medical or fraud detection contexts.",
        "What is the central limit theorem and why is it foundational in statistical inference?",
        "How do you design an A/B test to validate whether a new model yields statistically significant uplift?",
        "What are the primary assumptions of Ordinary Least Squares (OLS) linear regression?",
        "Explain the concept of SHAP and LIME values for model interpretability and explainability.",
        "How do you monitor machine learning models in production for data drift and concept drift?",
        "What is ensemble learning and what are the main differences between bagging and boosting?",
        "Explain how natural language processing tokenization, stemming, and lemmatization work."
    ],
    "Data Analyst": [
        "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN in SQL?",
        "How do group by and having clauses work together in SQL queries?",
        "How do you handle outliers in data visualization?",
        "Explain the difference between categorical and numerical variables.",
        "What are SQL window functions like ROW_NUMBER(), RANK(), and DENSE_RANK()?",
        "How do you design an executive dashboard to communicate critical KPI trends clearly?",
        "What is the difference between star schema and snowflake schema in data warehousing?",
        "How do you calculate Customer Lifetime Value (CLV) and Churn Rate using transactional data?",
        "Explain how you would write a SQL query to identify month-over-month revenue growth.",
        "What methods do you use to validate data quality and detect duplicates across merged sources?",
        "Explain correlation versus causation and how you communicate that distinction to business stakeholders.",
        "What are the key differences between OLTP and OLAP systems?",
        "How do you choose between a bar chart, line chart, scatter plot, and heatmap for distinct data stories?",
        "Explain how cohort analysis is structured and what insights it reveals about user retention.",
        "How do you handle skewed distributions and extreme values when reporting mean vs median?",
        "Describe how you use CTEs (Common Table Expressions) and subqueries to structure complex queries.",
        "How do you perform exploratory data analysis (EDA) on a newly ingested raw dataset?",
        "What is an ETL pipeline and what role does data transformation play in analytical workflows?",
        "Explain how you translate vague business questions into quantifiable analytical metrics.",
        "How do you calculate sample size and statistical power for a marketing conversion experiment?",
        "What are the differences between primary keys, foreign keys, and composite keys in data models?",
        "Describe how you ensure sensitive candidate or customer data complies with privacy regulations.",
        "How do you automate recurring analytical reports using SQL scripts, scheduled jobs, or BI tools?",
        "Explain how indexing in relational databases impacts query read performance versus write latency.",
        "How do you conduct root-cause analysis when an established business metric suddenly drops 20%?"
    ],
    "AI/ML Engineer": [
        "What is gradient descent and how does learning rate affect optimization?",
        "Explain the difference between Precision and Recall.",
        "What is transfer learning and when would you use it?",
        "How do Convolutional Neural Networks (CNNs) process image data?",
        "Explain the architecture of the Transformer model and the self-attention mechanism.",
        "What causes vanishing and exploding gradients in deep networks, and how are they mitigated?",
        "How do Recurrent Neural Networks (RNNs) and LSTMs handle sequential and time-series data?",
        "What is batch normalization and how does it accelerate deep neural network training?",
        "Explain the role of loss functions like Cross-Entropy and Mean Squared Error in model training.",
        "What is model quantization and pruning, and how do they optimize edge/production inference?",
        "Explain the differences between fine-tuning, LoRA (Low-Rank Adaptation), and prompt engineering for LLMs.",
        "How do vector databases and embedding search work in Retrieval-Augmented Generation (RAG) systems?",
        "What strategies do you employ to prevent hallucinations and ensure grounded outputs in generative AI?",
        "Explain how learning rate schedulers like Cosine Annealing improve convergence in deep learning.",
        "How do you package and deploy machine learning models using ONNX, TensorRT, or TorchScript?",
        "What are the key trade-offs between model latency, memory footprint, and prediction accuracy in production?",
        "Explain the concept of autoencoders and how they are used for anomaly detection and representation learning.",
        "How does distributed training work across multiple GPUs using DataParallel or DistributedDataParallel?",
        "What are Generative Adversarial Networks (GANs) and how do generator and discriminator networks interact?",
        "How do you design an automated continuous training and model re-evaluation pipeline (MLOps)?",
        "Explain the purpose of activation functions like ReLU, GELU, and Swish in deep neural networks.",
        "How do you evaluate generative AI applications where standard accuracy metrics are not applicable?",
        "What is temperature in LLM sampling and how does it balance determinism versus creativity?",
        "How do you profile GPU utilization, memory bottlenecks, and I/O bottlenecks during model training?",
        "Explain how semantic caching can reduce LLM API latency and operating costs in high-volume applications."
    ],
    "Product Manager": [
        "How do you prioritize features when resources are limited?",
        "Describe how you define key performance metrics for a new product launch.",
        "How do you handle conflicting user feedback during product discovery?",
        "Explain the RICE and Kano prioritization frameworks and when you apply each.",
        "How do you construct a product roadmap that balances short-term wins with long-term strategic bets?",
        "Describe your process for conducting user interviews and synthesizing qualitative insights into action.",
        "How do you write a comprehensive Product Requirements Document (PRD) for engineering and design teams?",
        "What is the difference between leading indicators and lagging indicators in product analytics?",
        "How do you handle scope creep when unexpected technical hurdles emerge close to a deadline?",
        "Describe how you run effective A/B tests and determine whether a feature experiment succeeded.",
        "How do you navigate difficult trade-offs between technical debt reduction and new feature delivery?",
        "What is a Minimum Viable Product (MVP) and how do you validate value hypotheses with minimal engineering?",
        "How do you establish alignment between engineering, sales, marketing, and executive stakeholders?",
        "Describe your approach to competitive analysis and market positioning for an emerging product.",
        "How do you determine product pricing and monetization models (e.g., freemium, tiered SaaS, usage-based)?",
        "What metrics do you track to measure user engagement, activation, retention, and referral?",
        "Explain how you handle a scenario where a newly released feature causes negative user metrics.",
        "How do you evaluate whether to build a capability in-house, buy a third-party tool, or partner?",
        "Describe how you define customer personas, empathy maps, and user journey flows.",
        "How do you manage stakeholder expectations when customer-requested features must be rejected?",
        "What is the North Star Metric and how do you ensure the entire cross-functional team rallies around it?",
        "Describe how you facilitate sprint planning, backlog refinement, and retrospectives with engineers.",
        "How do you measure product-market fit and what qualitative and quantitative signals indicate it?",
        "How do you communicate a major product pivot or strategy change to your team and customers?",
        "Describe a time when data contradicted your intuition and how you navigated the product decision."
    ]
}

INTERVIEW_TYPE_QUESTIONS = {
    "System Design Interview": [
        "How would you design a scalable URL shortener like TinyURL capable of handling billions of redirects?",
        "Explain the CAP theorem and the trade-offs between consistency and availability in distributed databases.",
        "How do load balancers distribute traffic across server clusters, and what routing algorithms are used?",
        "How would you design a distributed caching layer using Redis to mitigate database hot spots?",
        "Describe how database sharding and partitioning work to scale relational databases horizontally.",
        "How would you design a real-time notification service that scales to millions of concurrent push clients?",
        "Explain the differences between optimistic locking and pessimistic locking in concurrent systems.",
        "How would you design a rate limiter to protect public microservices from distributed denial of service?",
        "What is a Content Delivery Network (CDN) and how does edge caching improve global user latency?",
        "How would you design an idempotent payment processing system that prevents duplicate transactions?",
        "Explain the difference between strong consistency, eventual consistency, and read-after-write consistency.",
        "How would you design a distributed task queue or job scheduler for asynchronous background processing?",
        "What are the trade-offs between REST, GraphQL, and gRPC for inter-service and client communications?",
        "How do you handle leader election and distributed consensus using algorithms like Raft or Paxos?",
        "How would you design an observability platform that aggregates metrics, logs, and distributed traces?",
        "Describe how you would design a scalable feed system like Twitter or LinkedIn with fan-out on write.",
        "How do you handle schema migrations in high-availability production databases with zero downtime?",
        "Explain the circuit breaker pattern and how it prevents cascading failures across microservices.",
        "How would you design a distributed file storage and retrieval service like Amazon S3?",
        "What strategies do you use for disaster recovery, multi-region replication, and automated failover?"
    ],
    "Behavioral Interview": [
        "Tell me about a time you faced a significant obstacle on a project and how you overcame it.",
        "Describe a situation where you had a technical disagreement with a teammate and how you resolved it.",
        "Can you share an example of a project where requirements changed abruptly and how you adapted?",
        "Tell me about a time you made a mistake that affected production or the team, and what you learned.",
        "Describe a scenario where you had to prioritize multiple urgent deadlines under intense pressure.",
        "How do you deliver constructive feedback to peers or leadership when code or processes are lacking?",
        "Tell me about a time you took initiative to improve an existing process or tool without being asked.",
        "Describe a project where you collaborated with a difficult stakeholder and achieved a successful outcome.",
        "Can you tell me about a time you had to learn a completely new technology or domain very rapidly?",
        "Describe a situation where you mentored or helped an onboarding teammate succeed.",
        "Tell me about a time a project you worked on failed or fell short of expectations, and how you responded.",
        "Describe a situation where you had to persuade senior stakeholders to adopt your technical recommendation.",
        "Tell me about a time you had to balance building the ideal technical solution against strict time constraints.",
        "Describe a situation where you discovered a serious bug or security flaw close to a major release.",
        "Tell me about a time you worked on a team with diverse perspectives or conflicting priorities.",
        "Describe how you handle ambiguous tasks where clear guidelines or documentation were missing.",
        "Tell me about a proud accomplishment where your technical contribution drove measurable business value.",
        "Describe a time you had to advocate for technical debt cleanup or engineering quality to business leaders.",
        "Tell me about a time you received critical feedback that was difficult to hear and how you applied it.",
        "Describe an instance where you stepped outside your official role responsibilities to support a critical launch."
    ],
    "HR Interview": [
        "Tell me about yourself and what brought you to this point in your professional journey.",
        "What motivated you to apply for this role and what excites you about our company mission?",
        "What are your greatest professional strengths and an area you are actively working to improve?",
        "Where do you see yourself professionally in the next 3 to 5 years, and what skills do you hope to master?",
        "Describe your ideal company culture and the work environment in which you perform at your best.",
        "How do you maintain work-life balance and prevent burnout during high-demand project cycles?",
        "What kind of management style empowers you to do your most impactful and fulfilling work?",
        "How do you handle stress, constructive criticism, and setbacks in a collaborative workplace?",
        "What factors are most important to you when evaluating a new job opportunity or team culture?",
        "Tell me about a workplace value or principle that guides your everyday interactions with colleagues.",
        "How do you stay organized and manage your time effectively in remote or hybrid working environments?",
        "What are your salary and compensation expectations for this position based on your experience?",
        "Describe an experience that demonstrated your resilience and perseverance through a difficult period.",
        "What role do diversity, equity, and inclusion play in your vision of a high-performing team?",
        "How do you prefer to give and receive recognition for hard work and team achievements?",
        "Why are you looking to transition from your current position or previous role at this stage?",
        "What hobbies, creative pursuits, or activities outside of work keep you energized and grounded?",
        "How do you handle situations where your personal working style differs from your manager's style?",
        "What questions do you have for us regarding the team dynamics, growth path, or company trajectory?",
        "Describe a time you helped build an inclusive, supportive, and psychologically safe team culture."
    ]
}

GENERIC_QUESTIONS = [
    "Tell me about your technical background and key projects.",
    "What are your greatest technical strengths and areas for improvement?",
    "Describe a challenging problem you faced in a project and how you resolved it.",
    "How do you stay up-to-date with emerging tools and technologies in your field?",
    "Where do you see yourself professionally in the next 3 to 5 years?",
    "How do you approach learning complex new domain concepts under tight timelines?",
    "Describe your philosophy on balancing code quality and speed of execution.",
    "What tools and practices do you rely on to manage your personal productivity and focus?",
    "How do you break down a complex, ambiguous problem into actionable development milestones?",
    "Describe an instance where you successfully simplified an overly complicated process or architecture.",
    "What role does documentation play in your development workflow and knowledge-sharing strategy?",
    "How do you approach code reviews to ensure high standards while maintaining team velocity?",
    "Describe your experience working with cross-functional teams and non-technical stakeholders.",
    "What methodologies (e.g., Agile, Scrum, Kanban) have you found most effective and why?",
    "How do you handle unexpected changes in project scope or timeline constraints?",
    "What metrics do you use to evaluate whether a feature or project was truly successful?",
    "Describe a situation where you had to compromise on an architectural decision for business needs.",
    "How do you approach continuous testing and automated verification in your software projects?",
    "What has been the most technically challenging bug you have ever diagnosed and resolved?",
    "How do you ensure user privacy, system security, and data integrity in your everyday work?",
    "What strategies do you use to keep long-running codebases maintainable and free of severe technical debt?",
    "Describe how you evaluate third-party dependencies before introducing them into a production stack.",
    "What is your approach to post-incident postmortems and fostering a blameless engineering culture?",
    "How do you communicate technical risks and system limitations to non-technical business partners?",
    "What excites you most about the future of technology and engineering practices in your specialization?"
]


def generate_question_mock(job_role: str, interview_type: str, difficulty: str, skills: str = "") -> str:
    """Generates a fallback mock question based on job role, interview type, and skills."""
    type_qs = INTERVIEW_TYPE_QUESTIONS.get(interview_type, [])
    role_qs = QUESTIONS_BANK.get(job_role, GENERIC_QUESTIONS)
    combined = (type_qs + role_qs) if type_qs else role_qs

    # If candidate specified custom skills, check if any question matches skills
    if skills:
        skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
        for q in combined:
            if any(sk in q.lower() for sk in skill_list):
                return q

    return random.choice(combined) if combined else random.choice(GENERIC_QUESTIONS)


from app.services.answer_validator import validate_answer_meaningfulness, COMMON_TECH_TERMS, RE_BIG_O, RE_HTTP_STATUS, RE_SQL_QUERY

def evaluate_answer_mock(question_text: str, answer_text: str) -> dict:
    """Evaluates answer quality using grounded heuristics, relevance matching, and meaningfulness validation."""
    # Step 1: Meaningfulness validation
    val = validate_answer_meaningfulness(question_text, answer_text)
    if not val.is_valid:
        return {
            "score": 0,
            "technical_score": 0,
            "communication_score": 0,
            "relevance_score": 0,
            "completeness_score": 0,
            "feedback": (
                "The submitted response is unintelligible, empty, or contains no meaningful "
                "technical explanation addressing the question. Please provide a relevant and structured answer."
            ),
            "strengths": [],
            "improvements": [
                "Provide a coherent answer addressing the core question",
                "Explain the concept using standard technical terminology"
            ]
        }

    raw = answer_text.strip()
    words = raw.split()
    length = len(words)
    q_lower = question_text.lower()
    a_lower = raw.lower()

    # Step 2: Handle valid concise technical shortcuts (e.g. 'O(log n)', 'HTTP 404', 'A tuple is immutable')
    is_complexity_q = any(k in q_lower for k in ["complexity", "big-o", "big o", "time complexity", "space complexity", "runtime"])
    is_http_q = any(k in q_lower for k in ["http", "status code", "rest api", "404", "status"])
    is_sql_q = any(k in q_lower for k in ["sql", "query", "database", "select", "table"])

    if RE_BIG_O.match(raw):
        if is_complexity_q:
            tech = 95
            rel = 95
            comm = 80
            comp = 75
            score = round(0.40 * tech + 0.25 * rel + 0.20 * comp + 0.15 * comm)
            return {
                "score": score,
                "technical_score": tech,
                "communication_score": comm,
                "relevance_score": rel,
                "completeness_score": comp,
                "feedback": "Correct and concise asymptotic complexity answer. To make it even stronger, briefly explain the reasoning behind this bound.",
                "strengths": ["Accurate complexity identification", "Direct and concise"],
                "improvements": ["Elaborate on why this complexity arises during execution"]
            }
        else:
            # Complexity answered to a non-complexity question
            return {
                "score": 25,
                "technical_score": 20,
                "communication_score": 50,
                "relevance_score": 15,
                "completeness_score": 15,
                "feedback": "You provided an asymptotic complexity, but the question was not asking for a Big-O complexity bound.",
                "strengths": ["Valid notation"],
                "improvements": ["Address the specific requirements of the question"]
            }

    if RE_HTTP_STATUS.match(raw):
        if is_http_q:
            tech = 95
            rel = 95
            comm = 80
            comp = 75
            score = round(0.40 * tech + 0.25 * rel + 0.20 * comp + 0.15 * comm)
            return {
                "score": score,
                "technical_score": tech,
                "communication_score": comm,
                "relevance_score": rel,
                "completeness_score": comp,
                "feedback": "Accurate HTTP status code identified. Adding a brief explanation of when it is returned would provide complete context.",
                "strengths": ["Correct status code", "Direct answer"],
                "improvements": ["Explain the condition under which this code is returned"]
            }

    if RE_SQL_QUERY.match(raw):
        if is_sql_q:
            tech = 90
            rel = 95
            comm = 85
            comp = 80
            score = round(0.40 * tech + 0.25 * rel + 0.20 * comp + 0.15 * comm)
            return {
                "score": score,
                "technical_score": tech,
                "communication_score": comm,
                "relevance_score": rel,
                "completeness_score": comp,
                "feedback": "Syntactically structured SQL query provided that addresses the database requirement.",
                "strengths": ["Clean SQL syntax", "Direct query formulation"],
                "improvements": ["Explain index usage or query plan considerations"]
            }

    # Step 3: Compute keyword relevance and semantic overlap
    q_words = [w.strip("?,.:;\"'()[]{}").lower() for w in question_text.split() if len(w) > 3]
    stopwords = {"what", "which", "when", "where", "explain", "describe", "between", "difference", "using", "with", "from", "that", "this", "does", "have", "your"}
    q_keywords = [w for w in q_words if w not in stopwords]

    matched_keywords = [kw for kw in q_keywords if kw in a_lower]
    overlap_ratio = len(matched_keywords) / max(1, len(q_keywords))

    # Tech terms in answer
    tech_hits = [w for w in words if w.strip("?,.:;\"'()[]{}").lower() in COMMON_TECH_TERMS]
    tech_count = len(tech_hits)

    # Step 4: Detect fluent English answers that are completely off-topic
    if len(q_keywords) >= 2 and len(matched_keywords) == 0 and tech_count == 0:
        return {
            "score": 15,
            "technical_score": 10,
            "communication_score": 60,
            "relevance_score": 10,
            "completeness_score": 10,
            "feedback": "The response is grammatically formed, but it does not appear relevant to the question asked. Please address the specific technical topic.",
            "strengths": ["Grammatically structured answer"],
            "improvements": [
                "Directly address the concepts in the question",
                "Include core technical concepts relevant to the topic"
            ]
        }

    # Step 5: Grounded scoring based on relevance, technical depth, and completeness
    # Relevance score
    relevance_score = min(95, int(40 + overlap_ratio * 50 + min(15, tech_count * 3)))

    # Technical score
    technical_score = min(95, int(35 + min(40, tech_count * 8) + (20 if overlap_ratio > 0.3 else 5)))

    # Communication score (clarity, capitalization, sentence formation)
    has_sentence_structure = raw[0].isupper() and any(raw.endswith(p) for p in [".", "!", "?"])
    communication_score = 75 if not has_sentence_structure else 85
    if length > 25:
        communication_score = min(95, communication_score + 5)

    # Completeness score
    completeness_score = min(95, int(30 + min(40, length * 1.5) + (25 if overlap_ratio > 0.4 else 10)))

    # Concise one-liner high-quality bonus (e.g. "A tuple is immutable in Python.")
    if length <= 15 and overlap_ratio >= 0.3:
        technical_score = max(technical_score, 85)
        relevance_score = max(relevance_score, 88)
        completeness_score = max(completeness_score, 70)

    overall_score = round(
        0.40 * technical_score +
        0.25 * relevance_score +
        0.20 * completeness_score +
        0.15 * communication_score
    )

    # Construct contextual feedback
    if overall_score >= 80:
        feedback = "Strong answer! You explained the core concepts clearly and demonstrated good technical understanding."
        strengths = ["Accurate technical concepts", "Good conceptual clarity"]
        improvements = ["Could provide additional production trade-offs or edge-case handling"]
    elif overall_score >= 60:
        feedback = "Good foundation. You covered the main ideas, but expanding on specific implementation details or trade-offs would improve completeness."
        strengths = ["Direct answer addressing the topic", "Correct terminology used"]
        improvements = ["Elaborate on practical real-world applications", "Expand on underlying mechanics"]
    else:
        feedback = "Partial attempt. Your answer mentions related terms, but lacks sufficient technical depth and complete explanations."
        strengths = ["Identified some relevant keywords"]
        improvements = ["Provide a complete explanation of how and why the concept works", "Use more specific technical details"]

    return {
        "score": overall_score,
        "technical_score": technical_score,
        "communication_score": communication_score,
        "relevance_score": relevance_score,
        "completeness_score": completeness_score,
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements
    }

def generate_coding_feedback_mock(problem_title: str, language: str, source_code: str, status: str, score: float, passed: int, total: int) -> dict:
    """Generates mock AI coding feedback strictly grounded in execution results."""
    is_fully_correct = (status == "accepted" and score >= 100.0 and passed == total)

    if is_fully_correct:
        summary = f"Excellent job! Your {language} solution successfully passed all {total}/{total} test cases with a 100% score."
        correctness = f"Accepted: All {total} test cases passed correctly. The algorithm handles standard and boundary scenarios properly."
        strengths = [
            "Optimal logic and clear control flow",
            "Correct handling of inputs and boundary conditions",
            f"Idiomatic {language} syntax and clean structure"
        ]
        issues = ["No critical functional defects detected."]
        improvements = [
            "Consider adding inline comments to document tricky edge cases.",
            "Verify if constant-factor memory overhead can be further minimized."
        ]
    else:
        summary = f"Your {language} submission for '{problem_title}' finished with status '{status}' ({passed}/{total} tests passed, score: {score}/100)."
        correctness = f"Execution Status: {status.replace('_', ' ').capitalize()}. Passed {passed} out of {total} test cases. Review logical edge cases or execution constraints."
        strengths = [
            f"Structured attempt using {language}",
            "Solid initial framework and problem formulation"
        ]
        issues = [
            f"Execution result was {status} instead of accepted.",
            "Potential boundary condition mismatch or logical oversight on certain test inputs."
        ]
        improvements = [
            "Test your logic manually against small edge cases (e.g., empty arrays, single elements, negative values).",
            "Ensure loop indices and termination conditions are strictly bounded.",
            "Verify return types and state resets across multiple invocations."
        ]

    return {
        "summary": summary,
        "approach": f"Based on the submission, the code implements a direct solution for '{problem_title}' in {language}.",
        "correctness": correctness,
        "time_complexity": "O(N) (Estimated based on single-pass or structured traversal)",
        "space_complexity": "O(N) (Estimated auxiliary memory)",
        "strengths": strengths,
        "issues": issues,
        "improvements": improvements,
        "better_approach": "Review if an auxiliary hash structure, two-pointer window, or sorting step can streamline the algorithmic invariants.",
        "interview_tips": [
            "State your time and space complexity explicitly before writing code.",
            "Walk through a concrete sample input line-by-line before running tests.",
            "Proactively mention edge cases to the interviewer (e.g. empty inputs, duplicates)."
        ],
        "provider": "mock"
    }


def generate_coding_hint_mock(problem_title: str, category: str, difficulty: str, level: int) -> dict:
    """Generates deterministic, progressive AI hints (Levels 1, 2, and 3)."""
    cat = (category or "").lower()

    if "array" in cat or "string" in cat or "hash" in cat:
        topic_type = "arrays_hashing"
    elif "stack" in cat or "queue" in cat or "linked" in cat:
        topic_type = "linear_structures"
    elif "search" in cat or "sort" in cat or "recursion" in cat:
        topic_type = "search_sorting"
    elif "tree" in cat or "bst" in cat or "graph" in cat or "heap" in cat:
        topic_type = "trees_graphs"
    elif "dynamic" in cat or "dp" in cat or "greedy" in cat:
        topic_type = "dynamic_programming"
    else:
        topic_type = "general"

    if level == 1:
        # Level 1: Conceptual Guidance
        guidance = {
            "arrays_hashing": f"For '{problem_title}', think about the relationship between elements. Instead of repeatedly searching through all elements for every item, consider what information you can store to answer queries in constant time.",
            "linear_structures": f"For '{problem_title}', consider how the order of arrival matters. If you need Last-In-First-Out behavior, a stack is natural; for First-In-First-Out, consider a queue. Look for patterns where elements wait to be resolved.",
            "search_sorting": f"For '{problem_title}', identify whether the search space is monotonic or sorted. If an input is sorted or can be sorted, you can eliminate half of the remaining choices at each step.",
            "trees_graphs": f"For '{problem_title}', consider recursive decomposition. Can the problem for the root be solved if you already have the answers for the left and right subtrees?",
            "dynamic_programming": f"For '{problem_title}', look for overlapping subproblems. Does the optimal answer for size N depend on optimal answers for smaller subproblems (like N-1 or N-2)?",
            "general": f"For '{problem_title}', start by clarifying what state uniquely identifies a solution. Break the problem down into the smallest self-contained decision.",
        }
        return {
            "level": 1,
            "title": "Level 1 — Conceptual Guidance",
            "hint": guidance.get(topic_type, guidance["general"]),
            "key_takeaways": [
                "Formulate a clear mental model before jumping into code syntax.",
                "Identify the core invariant or relationship between input elements."
            ],
            "edge_cases": [
                "Empty collection or minimal valid input size.",
                "Input with identical or duplicate values."
            ],
            "provider": "mock"
        }

    elif level == 2:
        # Level 2: Approach Guidance
        guidance = {
            "arrays_hashing": f"Use a hash map or hash set to map values to their indices or frequencies. As you iterate through the collection once, check if the complementary value has already been recorded in the map.",
            "linear_structures": f"Maintain an auxiliary stack or pointer pair. Push elements or their indices onto the stack while maintaining monotonicity, and pop whenever a condition is violated or satisfied.",
            "search_sorting": f"Use a two-pointer binary search with `low` and `high` bounds. Compute `mid = low + (high - low) // 2` to prevent overflow, and adjust `low` or `high` based on the comparison.",
            "trees_graphs": f"Use depth-first search (DFS) with a helper function or breadth-first search (BFS) with a queue. Track visited nodes or subtree properties like depth and maximum path sum.",
            "dynamic_programming": f"Define `dp[i]` as the optimal answer for prefix of length `i`. Write out the base cases (e.g. `dp[0]`) and the transition equation combining previous results.",
            "general": f"Identify the appropriate data structure (hash table, two pointers, or auxiliary array) to avoid quadratic brute-force operations.",
        }
        return {
            "level": 2,
            "title": "Level 2 — Approach Guidance",
            "hint": guidance.get(topic_type, guidance["general"]),
            "key_takeaways": [
                "Select data structures that trade small memory for significant time savings.",
                "Maintain clear loop invariants throughout the iteration."
            ],
            "edge_cases": [
                "Handling negative values or extreme bounds.",
                "Single-element inputs where loops might not execute."
            ],
            "provider": "mock"
        }

    else:
        # Level 3: Detailed Guidance
        guidance = {
            "arrays_hashing": "Step 1: Initialize an empty hash map `seen`.\nStep 2: Iterate through the array with index `i` and element `x`.\nStep 3: Calculate target complement `needed = target - x`.\nStep 4: If `needed` exists in `seen`, return `[seen[needed], i]`.\nStep 5: Otherwise, record `seen[x] = i` and continue.",
            "linear_structures": "Step 1: Initialize an empty stack `st`.\nStep 2: Traverse each token or bracket in the string/array.\nStep 3: If it is an opening element, push it onto `st`.\nStep 4: If it is a closing element, verify `st` is non-empty and matches the top; if so, pop; otherwise, return false.\nStep 5: After iteration, the result is valid only if `st` is completely empty.",
            "search_sorting": "Step 1: Set `left = 0`, `right = len(arr) - 1`.\nStep 2: Loop while `left <= right`.\nStep 3: Calculate `mid = left + (right - left) // 2`.\nStep 4: If `arr[mid] == target`, return `mid`.\nStep 5: If `arr[mid] < target`, update `left = mid + 1`; else update `right = mid - 1`.\nStep 6: Return -1 if not found.",
            "trees_graphs": "Step 1: Base Case: If the current node is null, return appropriate default (e.g. null, 0, or true).\nStep 2: Recursively compute results for `left` and `right` subtrees.\nStep 3: Combine left and right results with the current node's value.\nStep 4: Return the aggregated result back up the recursion tree.",
            "dynamic_programming": "Step 1: Create a DP array `dp` of size `N + 1` filled with base values.\nStep 2: Initialize base cases `dp[0]` and `dp[1]`.\nStep 3: For `i` from 2 to `N`, compute `dp[i]` using the recurrence relation.\nStep 4: Return `dp[N]` as the final optimal solution.",
            "general": "Step 1: Validate input boundaries and handle empty cases.\nStep 2: Initialize variables and tracking structures.\nStep 3: Execute core traversal loop maintaining problem invariants.\nStep 4: Construct and return final result.",
        }
        return {
            "level": 3,
            "title": "Level 3 — Detailed Guidance",
            "hint": guidance.get(topic_type, guidance["general"]),
            "key_takeaways": [
                "Follow the step-by-step state transitions rigorously.",
                "Ensure termination criteria are watertight to avoid infinite loops."
            ],
            "edge_cases": [
                "Off-by-one boundary index errors.",
                "Empty collection or uninitialized state."
            ],
            "provider": "mock"
        }


def generate_coding_explanation_mock(problem_title: str, category: str, difficulty: str, description: str = "") -> dict:
    """Generates an educational deep-dive explanation of optimal algorithms and concepts."""
    cat = (category or "").lower()

    if "array" in cat or "hash" in cat:
        intuition = f"The core intuition for '{problem_title}' is leveraging constant-time hash lookups to replace an exhaustive search, trading O(N) extra space for O(N) linear time."
        brute_force = "The naive approach uses two nested loops, checking every pair or subset. This results in quadratic O(N^2) time complexity, which times out on large inputs (e.g. N = 10^5)."
        optimized = "By storing previously observed elements in a hash map as we iterate, each lookup is performed in average O(1) time. In a single pass, we can determine the answer."
        step_by_step = [
            "Initialize an auxiliary hash table to store elements or their indices.",
            "Iterate through the collection from left to right.",
            "Check if the required counterpart or condition exists in the hash table.",
            "If found, return the resolved indices or values immediately.",
            "Otherwise, record the current element in the hash table and continue."
        ]
        time_comp = "O(N) - Linear time because we perform a single pass over the array with O(1) hash map operations."
        space_comp = "O(N) - Linear space in the worst case to store up to N elements in the hash map."
        common_mistakes = [
            "Reusing the same element twice when problem constraints prohibit it.",
            "Assuming the array is sorted when it is not.",
            "Overlooking duplicate keys or colliding values."
        ]
        edge_cases = [
            "Array with minimum length (e.g. 2 elements).",
            "Negative numbers and zero.",
            "Large numbers near integer limits."
        ]
    elif "string" in cat:
        intuition = f"The challenge in '{problem_title}' is efficiently processing characters while maintaining order or in-place memory guarantees."
        brute_force = "Creating new substring copies repeatedly leads to excessive memory allocations and O(N^2) string concatenation overhead."
        optimized = "Use a two-pointer technique moving inward from the boundaries, modifying or comparing characters in-place with O(1) auxiliary space."
        step_by_step = [
            "Initialize two pointers: `left = 0` and `right = length - 1`.",
            "While `left < right`, inspect or swap characters at both indices.",
            "Increment `left` and decrement `right` inward.",
            "Terminate when pointers meet or cross."
        ]
        time_comp = "O(N) - Linear time as each character is processed at most once."
        space_comp = "O(1) - Constant auxiliary space when modifying in-place."
        common_mistakes = [
            "Creating extra string buffers when in-place modification is required.",
            "Off-by-one errors in pointer initialization (`length` vs `length - 1`).",
            "Not handling case sensitivity or non-alphanumeric characters."
        ]
        edge_cases = [
            "Empty string or single character string.",
            "All characters identical.",
            "Palindromic or already symmetric inputs."
        ]
    elif "stack" in cat or "queue" in cat:
        intuition = f"The core insight for '{problem_title}' is that nested or paired elements obey Last-In-First-Out (LIFO) or First-In-First-Out (FIFO) ordering."
        brute_force = "Searching backwards repeatedly through past elements on every step yields O(N^2) complexity."
        optimized = "A stack maintains active unresolved elements. When a matching or closing element arrives, the top element is popped and verified in O(1) time."
        step_by_step = [
            "Initialize an empty stack.",
            "Iterate through each token in the input sequence.",
            "Push opening tokens onto the stack.",
            "For closing tokens, verify the stack is non-empty and matches the top token.",
            "Pop the matched token and proceed.",
            "Verify the stack is empty after the entire sequence is processed."
        ]
        time_comp = "O(N) - Each token is pushed and popped at most once."
        space_comp = "O(N) - Worst case space when all tokens are pushed before any are popped."
        common_mistakes = [
            "Popping from an empty stack leading to runtime errors.",
            "Forgetting to check if the stack is completely empty at the end.",
            "Mismatched bracket types."
        ]
        edge_cases = [
            "Starting with a closing bracket.",
            "Only opening brackets without closers.",
            "Empty input string."
        ]
    elif "search" in cat or "sort" in cat:
        intuition = f"The key intuition for '{problem_title}' is exploiting monotonicity to discard half of the search space at each iteration."
        brute_force = "A linear scan inspects every element one by one in O(N) time."
        optimized = "Binary search divides the interval in half on each step, achieving logarithmic O(log N) runtime."
        step_by_step = [
            "Set search boundaries `low = 0` and `high = length - 1`.",
            "While `low <= high`, calculate middle index `mid = low + (high - low) // 2`.",
            "Compare `array[mid]` with the target value.",
            "If equal, return `mid`.",
            "If smaller, narrow search space to the right: `low = mid + 1`.",
            "If larger, narrow search space to the left: `high = mid - 1`."
        ]
        time_comp = "O(log N) - Logarithmic time as the search space is halved at each step."
        space_comp = "O(1) - Constant auxiliary space for pointer variables."
        common_mistakes = [
            "Integer overflow from `(low + high) // 2` in typed languages.",
            "Infinite loops from using `low < high` without proper pointer updates.",
            "Missing the target when it resides at the boundary indices."
        ]
        edge_cases = [
            "Target not present in array.",
            "Target at the very first or very last position.",
            "Array of size 1."
        ]
    elif "tree" in cat or "graph" in cat:
        intuition = f"For '{problem_title}', hierarchical structures lend themselves to recursive divide-and-conquer traversals."
        brute_force = "Traversing the entire structure multiple times for each query."
        optimized = "Single-pass Depth-First Search (DFS) or Breadth-First Search (BFS) computes and propagates subtree properties."
        step_by_step = [
            "Establish the base case: return immediately on reaching a null node or leaf.",
            "Recursively traverse child subtrees.",
            "Combine child results with the current node's value.",
            "Return the computed metric to the parent caller."
        ]
        time_comp = "O(N) - Every node in the tree/graph is visited exactly once."
        space_comp = "O(H) - Auxiliary call stack space proportional to height H (O(log N) balanced, O(N) skewed)."
        common_mistakes = [
            "Forgetting the null check base case leading to null pointer exceptions.",
            "Not handling skewed tree structures.",
            "Conflating pre-order, in-order, and post-order logic."
        ]
        edge_cases = [
            "Empty tree (root is null).",
            "Single node tree.",
            "Completely skewed tree (linked-list shape)."
        ]
    elif "dynamic" in cat or "dp" in cat:
        intuition = f"For '{problem_title}', breaking the overall problem into overlapping subproblems allows storing intermediate results to avoid redundant work."
        brute_force = "Plain recursion recalculates the same subproblems repeatedly, exploding into exponential O(2^N) time."
        optimized = "Memoization (top-down) or tabulation (bottom-up) stores solved subproblems in a DP table, reducing time to polynomial."
        step_by_step = [
            "Define the state `dp[i]` representing the solution for subproblem of size `i`.",
            "Determine the base cases (e.g. `dp[0]` and `dp[1]`).",
            "Formulate the transition relation combining smaller subproblems.",
            "Iteratively populate the table up to the desired target.",
            "Return the final state `dp[N]`."
        ]
        time_comp = "O(N) - Each state is computed exactly once."
        space_comp = "O(N) - Storing the DP array (or O(1) if optimized to keep only the last few variables)."
        common_mistakes = [
            "Incorrect base case initialization.",
            "Off-by-one errors in table size or loop boundaries.",
            "Not recognizing overlapping subproblems."
        ]
        edge_cases = [
            "N = 0 or N = 1 base limits.",
            "Negative step sizes or constraints.",
            "Memory limits on very large inputs."
        ]
    else:
        intuition = f"Break down '{problem_title}' into basic logical building blocks, validating invariants at every step."
        brute_force = "Exhaustive simulation without pruning."
        optimized = "Targeted iteration with early termination and minimal auxiliary storage."
        step_by_step = [
            "Validate input parameters and handle edge cases.",
            "Initialize state variables.",
            "Execute main algorithmic process.",
            "Return the validated result."
        ]
        time_comp = "O(N) - Proportional to input size."
        space_comp = "O(1) - Constant auxiliary memory."
        common_mistakes = ["Not validating edge conditions."]
        edge_cases = ["Empty input or single element."]

    interview_tips = [
        "Communicate your thought process out loud before writing any code.",
        "State the brute-force approach first, then explain why and how you optimize it.",
        "Always discuss Time and Space complexity trade-offs explicitly.",
        "Write clean, readable variable names and ask clarifying questions about constraints."
    ]

    return {
        "title": problem_title,
        "difficulty": difficulty,
        "category": category,
        "intuition": intuition,
        "brute_force": brute_force,
        "optimized_approach": optimized,
        "step_by_step": step_by_step,
        "time_complexity": time_comp,
        "space_complexity": space_comp,
        "common_mistakes": common_mistakes,
        "edge_cases": edge_cases,
        "interview_tips": interview_tips,
        "provider": "mock"
    }


def generate_communication_feedback_mock(question_text: str, answer_text: str) -> dict:
    """Generates mock qualitative communication feedback based on answer length."""
    words = answer_text.strip().split() if answer_text else []
    length = len(words)

    if length == 0:
        return {
            "directness": "No answer was provided, so directness cannot be assessed.",
            "structure": "No content to evaluate for structure.",
            "conciseness": "No content was submitted.",
            "suggestion": "Provide a complete answer that directly addresses the question asked.",
        }
    elif length < 15:
        return {
            "directness": "The answer addresses the question but lacks supporting detail.",
            "structure": "The response is too brief to identify a clear structure.",
            "conciseness": "The answer is very concise — consider expanding with an example.",
            "suggestion": "Add one concrete example or explanation to support your main point.",
        }
    elif length < 60:
        return {
            "directness": "The answer directly addresses the core of the question.",
            "structure": "The response has a recognisable main point with some supporting context.",
            "conciseness": "The answer length is appropriate for this type of question.",
            "suggestion": "Consider ending with a brief summary sentence to reinforce your main point.",
        }
    else:
        return {
            "directness": "The answer is comprehensive and addresses the question with detail.",
            "structure": "The response demonstrates a clear progression of ideas.",
            "conciseness": "The answer is detailed — ensure every sentence adds value.",
            "suggestion": "Review whether any sentences can be condensed without losing meaning.",
        }


TOPIC_VARIATION_TEMPLATES = [
    "Could you explain key principles of {topic} and how you apply them as a {role}?",
    "What are common architectural patterns, trade-offs, and pitfalls when working with {topic}?",
    "How do you approach debugging, profiling, and optimizing performance in {topic}?",
    "Can you describe an end-to-end implementation where you utilized {topic} to solve a complex problem?",
    "How does {topic} scale in high-load production environments, and how do you ensure reliability?",
    "What security considerations and best practices should be observed when implementing {topic}?",
    "Compare {topic} with viable alternative technologies or approaches in a {role} workflow.",
    "How do you test and maintain code or systems built around {topic} across the software lifecycle?",
]

FALLBACK_SESSION_TEMPLATES = [
    "How do you handle technical debt, code reviews, and maintaining engineering standards as a {role}?",
    "Describe a critical production incident or failure you handled and the steps taken to mitigate and prevent it.",
    "How do you collaborate with cross-functional partners (e.g., designers, product managers, DevOps) to deliver outcomes?",
    "What metrics, observability tools, and logging strategies do you prioritize for systems in your domain?",
    "Explain your approach to estimating project timelines and managing shifting stakeholder requirements.",
    "How do you ensure data integrity, resilience, and fault tolerance in your technical solutions?",
    "Describe a situation where you had to make a difficult architectural trade-off under strict deadlines.",
    "How do you mentor junior engineers and foster technical excellence within your engineering organization?",
    "What strategies do you use for automated testing (unit, integration, regression) to ensure system reliability?",
    "How do you evaluate and safely adopt new frameworks, libraries, or methodologies in existing codebases?",
    "Can you discuss your approach to continuous integration, delivery pipelines, and zero-downtime deployments?",
    "Describe how you design secure APIs and protect sensitive data according to industry compliance standards.",
    "Question {seq}: Elaborate on your problem-solving methodology when tackling an ambiguous, poorly specified feature request as a {role}.",
    "Question {seq}: What strategies do you employ when refactoring legacy modules without degrading existing unit coverage?",
    "Question {seq}: Describe how you conduct capacity planning and resource allocation for high-throughput cloud microservices."
]


def generate_adaptive_question_mock(
    job_role: str,
    interview_type: str,
    difficulty: str,
    skills: str = "",
    previous_questions: list = None,
    last_answer_context: dict = None,
    topics_covered: list = None,
    under_covered_topics: list = None,
    weak_areas: list = None,
    category: str = None,
) -> dict:
    """
    Generates a fallback mock adaptive question avoiding previously asked questions
    and prioritizing under-covered topics, weak areas, and candidate skills.
    Guarantees no duplicate questions in extended sessions up to 20+ questions.
    Returns a dict with 'question', 'difficulty', 'topic', 'category', and 'reason'.
    """
    prev_set = set()
    if previous_questions:
        for q in previous_questions:
            if q:
                prev_set.add(" ".join(q.lower().strip().split()))

    type_qs = INTERVIEW_TYPE_QUESTIONS.get(interview_type, [])
    role_qs = QUESTIONS_BANK.get(job_role, [])

    # Assemble candidate pool prioritizing interview type and role questions
    if type_qs:
        all_candidates = type_qs + role_qs + GENERIC_QUESTIONS
    else:
        all_candidates = role_qs + GENERIC_QUESTIONS

    # Filter candidates to avoid previously asked questions
    available = [
        q for q in all_candidates
        if " ".join(q.lower().strip().split()) not in prev_set
    ]

    selected_topic = job_role
    selected_q = None

    # Priority target topics: weak areas first, then under-covered topics, then candidate skills
    candidate_topics = (weak_areas or []) + (under_covered_topics or []) + ([s.strip() for s in skills.split(",") if s.strip()] if skills else [])

    if candidate_topics:
        for target_top in candidate_topics:
            target_str = str(target_top).strip()
            if not target_str:
                continue
            # Search available questions matching target_top
            matches = [q for q in available if target_str.lower() in q.lower()]
            if matches:
                selected_q = matches[0]
                selected_topic = target_str
                break
            else:
                # Iterate over variation templates for target_top to find an unasked question
                for tmpl in TOPIC_VARIATION_TEMPLATES:
                    candidate_q = tmpl.format(topic=target_str, role=job_role)
                    if " ".join(candidate_q.lower().strip().split()) not in prev_set:
                        selected_q = candidate_q
                        selected_topic = target_str
                        break
                if selected_q:
                    break

    if not selected_q:
        if available:
            selected_q = available[0]
            for word in ["python", "sql", "rest", "mvc", "data", "learning", "trees", "join", "gradient", "docker", "react", "aws", "kafka", "redis", "transformer", "metric", "roadmap", "architecture", "security"]:
                if word in selected_q.lower():
                    selected_topic = word.capitalize()
                    break
        else:
            # Fallback when all standard questions have been used
            seq_num = len(previous_questions or []) + 1
            for tmpl in FALLBACK_SESSION_TEMPLATES:
                candidate_q = tmpl.format(role=job_role, seq=seq_num)
                if " ".join(candidate_q.lower().strip().split()) not in prev_set:
                    selected_q = candidate_q
                    selected_topic = f"{job_role} Practices"
                    break

            if not selected_q:
                selected_q = f"Question {seq_num}: Could you share advanced strategies and lessons learned in your work as a {job_role}?"
                selected_topic = f"{job_role} Practices"

    cat = category or interview_type or "Technical Interview"

    return {
        "question": selected_q,
        "difficulty": difficulty,
        "topic": selected_topic,
        "category": cat,
        "reason": f"Mock adaptive question covering {selected_topic} at {difficulty} level for {cat}."
    }


def generate_interview_intelligence_summary_mock(
    job_role: str,
    interview_type: str,
    difficulty: str,
    overall_score: float,
    category_scores: dict,
    topic_performance: list,
    strengths: list,
    improvement_areas: list,
) -> str:
    """Generates a fallback qualitative summary based strictly on deterministic evaluation metrics."""
    score_str = f"{round(overall_score, 1)}/100"
    str_summary = ", ".join(strengths[:2]) if strengths else "consistent responses"
    imp_summary = ", ".join(improvement_areas[:2]) if improvement_areas else "further technical elaboration"

    return (
        f"In this {difficulty} level {interview_type} for the {job_role} position, "
        f"you achieved an overall performance score of {score_str}. "
        f"Key strengths demonstrated during the interview include {str_summary}. "
        f"To improve performance in future sessions, focus on addressing {imp_summary}."
    )



