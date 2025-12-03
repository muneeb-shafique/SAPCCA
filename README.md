<div align="center">

  <img src="https://img.icons8.com/clouds/200/000000/chat.png" alt="SAPCCA Logo" width="200" height="200" />

  <h1>Secure AI-Powered Campus Chat Application (SAPCCA)</h1>
  
  <p>
    <strong>A Next-Gen Communication Platform for Universities</strong>
    <br />
    Integrating <em>Computer Networks</em>, <em>Data Science</em>, and <em>Data Structures & Algorithms</em>.
  </p>

  <p>
    <a href="#setup">
      <img src="https://img.shields.io/badge/Setup-Guide-blue?style=for-the-badge&logo=python" alt="Setup Guide" />
    </a>
    <a href="#features">
      <img src="https://img.shields.io/badge/Features-AI%20%26%20Security-success?style=for-the-badge&logo=security" alt="Features" />
    </a>
    <a href="#dsa">
      <img src="https://img.shields.io/badge/Core-DSA%20Optimized-orange?style=for-the-badge&logo=algorithms" alt="DSA" />
    </a>
  </p>

  <p>
    Developed by <strong>Institute of Data Science</strong> Students<br>
    <em>University of Engineering and Technology</em>
  </p>
</div>

<hr />

<details>
  <summary><strong>Table of Contents (Click to Expand)</strong></summary>
  <ol>
    <li><a href="#about">About the Project</a></li>
    <li><a href="#architecture">System Architecture</a></li>
    <li><a href="#dsa-integration">DSA Integration (Core Logic)</a></li>
    <li><a href="#ai-modules">AI & Data Science Modules</a></li>
    <li><a href="#screenshots">UI Screenshots</a></li>
    <li><a href="#tech-stack">Tech Stack</a></li>
    <li><a href="#installation">Installation & Setup</a></li>
    <li><a href="#usage">Usage Guide</a></li>
    <li><a href="#team">Development Team</a></li>
  </ol>
</details>

<hr />

<h2 id="about">1. 🚀 About the Project</h2>
<p>
  <strong>SAPCCA</strong> solves the problem of scattered and insecure communication tools in university environments. Unlike generic platforms (WhatsApp, Messenger), SAPCCA is a controlled, campus-authenticated ecosystem designed for academic integrity and privacy.
</p>
<p>
  It features <strong>End-to-End Encryption (AES-256)</strong>, real-time <strong>WebSocket messaging</strong>, and powerful <strong>AI agents</strong> that monitor sentiment and block spam in real-time.
</p>

<h2 id="architecture">2. 🏗️ System Architecture</h2>
<p>The system follows a robust Client-Server architecture designed to handle <strong>10,000+ concurrent users</strong>.</p>

<table width="100%">
  <thead>
    <tr>
      <th align="left">Layer</th>
      <th align="left">Description</th>
      <th align="left">Protocol/Tech</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Frontend Client</strong></td>
      <td>Responsive Web Interface for Chat, Groups, and Dashboards.</td>
      <td>HTML5, CSS3, JS</td>
    </tr>
    <tr>
      <td><strong>Network Layer</strong></td>
      <td>Secure transport channel ensuring low latency (<200ms).</td>
      <td>HTTPS, WSS (WebSockets)</td>
    </tr>
    <tr>
      <td><strong>Backend API</strong></td>
      <td>Handles Auth, Routing, and API Logic.</td>
      <td>Python (Flask/Django)</td>
    </tr>
    <tr>
      <td><strong>AI Engine</strong></td>
      <td>Processes text for sentiment and spam patterns.</td>
      <td>Scikit-Learn, NLP, BERT</td>
    </tr>
    <tr>
      <td><strong>Data Layer</strong></td>
      <td>Persistent storage for logs, users, and messages.</td>
      <td>PostgreSQL / MongoDB</td>
    </tr>
  </tbody>
</table>

<h2 id="dsa-integration">3. 🧠 DSA Integration (Algorithms)</h2>
<p>We utilized advanced Data Structures to ensure O(1) lookups and efficient networking.</p>

<table width="100%">
  <thead>
    <tr>
      <th width="20%">Feature</th>
      <th width="20%">Data Structure</th>
      <th width="60%">Implementation Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Search Engine</strong></td>
      <td><code>Trie (Prefix Tree)</code></td>
      <td>Used for the search bar to provide <strong>instant auto-complete</strong> functionality for usernames and groups. Performance: O(L) where L is the length of the string.</td>
    </tr>
    <tr>
      <td><strong>Session Mgmt</strong></td>
      <td><code>Hash Map</code></td>
      <td>Stores active user sessions and chat indexing for <strong>O(1) access time</strong>, reducing database load during high traffic.</td>
    </tr>
    <tr>
      <td><strong>Friend System</strong></td>
      <td><code>Graph (Adjacency List)</code></td>
      <td>Models relationships between students. Nodes represent users, and edges represent friendship status.</td>
    </tr>
    <tr>
      <td><strong>Message Queue</strong></td>
      <td><code>Priority Queue</code></td>
      <td>Ensures that system alerts and admin broadcasts are delivered before standard chat messages during network congestion.</td>
    </tr>
  </tbody>
</table>

<h2 id="ai-modules">4. 🤖 AI & Data Science Modules</h2>
<p>The application is guarded by two active Machine Learning models:</p>

<ul>
  <li>
    <strong>Sentiment Analysis Agent:</strong>
    <br>
    <em>Model:</em> Logistic Regression / Fine-tuned BERT.
    <br>
    <em>Function:</em> Analyzes incoming messages to detect abusive content or distress. Data is visualized on the Admin Dashboard.
  </li>
  <br>
  <li>
    <strong>Spam Detection Agent:</strong>
    <br>
    <em>Model:</em> TF-IDF Feature Extraction + Naive Bayes Classifier.
    <br>
    <em>Function:</em> Automatically flags spam messages, phishing URLs, and bot-like behavior. Assigns a "Spam Score" to users.
  </li>
</ul>

<h2 id="screenshots">5. 📸 UI Screenshots</h2>


<table width="100%">
  <tr>
    <td width="50%">
      <h4 align="center">Login & Authentication</h4>
      <img src="Preview/login.jpg" alt="Login Page" width="100%" />
    </td>
    <td width="50%">
      <h4 align="center">Real-Time Chat Interface</h4>
      <img src="Preview/chat.jpg" alt="Chat Window" width="100%" />
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h4 align="center">Admin Analytics Dashboard</h4>
      <img src="Preview/dashboard.jpg" alt="Analytics" width="100%" />
    </td>
    <td width="50%">
      <h4 align="center">Friends Management</h4>
      <img src="Preview/friends.jpg" alt="Media Sharing" width="100%" />
    </td>
  </tr>
</table>

<h2 id="tech-stack">6. 🛠️ Tech Stack</h2>

<p>
  <img src="https://img.shields.io/badge/Language-Python_3.10+-yellow?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/Frontend-HTML5_%2F_CSS3_%2F_JS-orange?style=flat-square&logo=html5" />
  <img src="https://img.shields.io/badge/Framework-Flask_%2F_Django-green?style=flat-square&logo=django" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL-blue?style=flat-square&logo=postgresql" />
  <img src="https://img.shields.io/badge/Realtime-Socket.IO-black?style=flat-square&logo=socket.io" />
  <img src="https://img.shields.io/badge/AI-Scikit_Learn-orange?style=flat-square&logo=scikitlearn" />
</p>

<h2 id="installation">7. ⚙️ Installation & Setup</h2>

<p>Follow these steps to set up the SAPCCA environment locally.</p>

<h3>Prerequisites</h3>
<ul>
  <li>Python 3.10 or higher</li>
  <li>PostgreSQL or MongoDB installed and running</li>
  <li>Node.js (optional, if using specific frontend frameworks)</li>
</ul>

<h3>Step 1: Clone the Repository</h3>
<pre><code>git clone https://github.com/muneeb-shafique/SAPCCA/
cd SAPCCA</code></pre>

<h3>Step 2: Create Virtual Environment</h3>
<h4>Windows</h4>
<pre><code>python -m venv venv
venv\Scripts\activate</code></pre>

<h4>Mac/Linux</h4>
<pre><code>python3 -m venv venv
source venv/bin/activate</code></pre>

<h3>Step 3: Install Dependencies</h3>
<p>We have separated core requirements from AI requirements for lighter installs.</p>
<pre><code>pip install -r requirements.txt</code></pre>

<details>
  <summary><strong>View sample <code>requirements.txt</code></strong></summary>
  <pre><code>flask
flask-socketio
flask-sqlalchemy
psycopg2-binary
scikit-learn
pandas
numpy
nltk
spacy
gunicorn
eventlet</code></pre>
</details>

<h3>Step 4: Environment Configuration</h3>
<p>Create a <code>.env</code> file in the root directory:</p>
<pre><code>SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:password@localhost/sapcca_db
AES_KEY=your_encryption_key
DEBUG=True</code></pre>

<h3>Step 5: Database Migration & Run</h3>
<h4>Initialize Database</h4>
<pre><code>flask db init
flask db migrate
flask db upgrade</code></pre>
<h4>Run the Server</h4>
<pre><code>python app.py</code></pre>

<p><em>The server will start at <code>http://127.0.0.1:5000</code></em></p>

<h2 id="usage">8. 📖 Usage Guide</h2>
<ol>
  <li><strong>Registration:</strong> Use your <code>@uet.edu.pk</code> email to register.</li>
  <li><strong>Add Friends:</strong> Search for users using the Trie-powered search bar and send requests.</li>
  <li><strong>Chat:</strong> Once accepted, click a friend to start a secure WebSocket session.</li>
  <li><strong>Groups:</strong> Go to the "Groups" tab to create a study group.</li>
  <li><strong>Admin:</strong> Log in with admin credentials to view the Sentiment Analysis heatmaps.</li>
</ol>

<h2 id="team">9. 👥 Development Team</h2>

<table width="100%">
  <thead>
    <tr>
      <th>Name</th>
      <th>Roll No</th>
      <th>Role</th>
      <th>GitHub</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Muneeb Shafique</strong></td>
      <td>2024-DS-36</td>
      <td>Lead Developer / Frontend + Backend Developer</td>
      <td><a href="https://github.com/muneeb-shafique/">@muneeb</a></td>
    </tr>
    <tr>
      <td><strong>Huzaifa</strong></td>
      <td>2024-DS-47</td>
      <td>Network Engineer</td>
      <td><a href="#">@huzaifa</a></td>
    </tr>
    <tr>
      <td><strong>Dayan</strong></td>
      <td>2024-DS-24</td>
      <td>ML Trainer</td>
      <td><a href="#">@dayan</a></td>
    </tr>
  </tbody>
</table>

<br>

<div align="center">
  <p>
    Dated: 11/27/25 | Institute of Data Science, UET
  </p>
  <img src="https://img.shields.io/badge/Status-Active_Development-brightgreen" />
  <img src="https://img.shields.io/badge/License-MIT-blue" />
</div>
