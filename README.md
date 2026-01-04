<div align="center">

  <img src="https://img.icons8.com/clouds/200/000000/chat.png" alt="SAPCCA Logo" width="200" height="200" />

  <h1>Secure AI-Powered Campus Chat Application (SAPCCA)</h1>
  
  <p>
    <strong>A Next-Gen Communication & Learning Platform for Universities</strong>
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
    <li><a href="#features">Key Features & Modules</a></li>
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
  <strong>SAPCCA</strong> solves the problem of scattered and insecure communication tools in university environments. Unlike generic platforms (WhatsApp, Messenger), SAPCCA is a controlled, campus-authenticated ecosystem designed for academic integrity, privacy, and seamless classroom management.
</p>
<p>
  It features <strong>End-to-End Encryption (AES-256)</strong>, real-time <strong>WebSocket messaging</strong>, powerful <strong>AI agents</strong> for moderation, and a full-fledged <strong>Learning Management System (LMS)</strong> for classes and assignments.
</p>

<h2 id="features">2. ✨ Key Features & Modules</h2>

<h3>🎓 Classes & Assignments System</h3>
<p>A comprehensive module for faculty and students to manage academic activities.</p>
<ul>
    <li><strong>Class Workspaces:</strong> Dedicated environments for each course with subject-specific sub-groups.</li>
    <li><strong>Assignment Management:</strong> Faculty can create assignments with attachments, due dates, and points. Students can upload submissions (files/text) directly within the app.</li>
    <li><strong>Grading & Feedback:</strong> Built-in grading interface for teachers to review submissions, assign grades, and provide feedback.</li>
    <li><strong>PDF Reports:</strong> Automated generation of professional class performance reports using <code>ReportLab</code>.</li>
</ul>

<h3>🎛️ Teacher Command Center</h3>
<p>An exclusive dashboard for faculty members to monitor and manage their academic ecosystem.</p>
<ul>
    <li><strong>Real-time Analytics:</strong> Visual metrics for active classes, enrolled students, and system health.</li>
    <li><strong>Live Activity Feed:</strong> Monitors recent submissions, logins, and system events.</li>
    <li><strong>Quick Actions:</strong> One-click tools to enroll students, revoke access, or broadcast system-wide alerts.</li>
    <li><strong>Security Alerts:</strong> Logs unauthorized access attempts or system anomalies.</li>
</ul>

<h3>💬 Secure Communication</h3>
<ul>
    <li><strong>Real-Time Chat:</strong> Powered by Socket.IO for instant messaging.</li>
    <li><strong>Group & Private Chats:</strong> Create study groups or chat 1-on-1 with friends.</li>
    <li><strong>Multimedia Support:</strong> Send images, documents, and voice messages.</li>
</ul>

<h2 id="architecture">3. 🏗️ System Architecture</h2>
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
      <td>Responsive Web Interface (Dashboard, Chat, Classes).</td>
      <td>HTML5, TailwindCSS, JS</td>
    </tr>
    <tr>
      <td><strong>Network Layer</strong></td>
      <td>Secure transport channel ensuring low latency (<200ms).</td>
      <td>HTTPS, WSS (WebSockets)</td>
    </tr>
    <tr>
      <td><strong>Backend API</strong></td>
      <td>Handles Auth, Routing, Classes, and API Logic.</td>
      <td>Python (Flask)</td>
    </tr>
    <tr>
      <td><strong>AI Engine</strong></td>
      <td>Processes text/images for moderation.</td>
      <td>Transformers, PyTorch, Scikit-Learn</td>
    </tr>
    <tr>
      <td><strong>Data Layer</strong></td>
      <td>Persistent storage for logs, users, classes, and messages.</td>
      <td>PostgreSQL (SQLAlchemy)</td>
    </tr>
  </tbody>
</table>

<h2 id="dsa-integration">4. 🧠 DSA Integration (Algorithms)</h2>
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
      <td><strong>Student Ranking</strong></td>
      <td><code>Merge Sort</code></td>
      <td>Used in <strong>Performance Reports</strong> to sort students by grades efficiently (O(N log N)). Implemented in `Backend/DSA/performance.py`.</td>
    </tr>
    <tr>
      <td><strong>Search Engine</strong></td>
      <td><code>Trie (Prefix Tree)</code></td>
      <td>Used for the search bar to provide <strong>instant auto-complete</strong> functionality for usernames and groups. Performance: O(L).</td>
    </tr>
    <tr>
      <td><strong>Session Mgmt</strong></td>
      <td><code>Hash Map</code></td>
      <td>Stores active user sessions and chat indexing for <strong>O(1) access time</strong>, reducing database load during high traffic.</td>
    </tr>
    <tr>
      <td><strong>Message Queue</strong></td>
      <td><code>Priority Queue</code></td>
      <td>Ensures that system alerts and admin broadcasts are delivered before standard chat messages during network congestion.</td>
    </tr>
  </tbody>
</table>

<h2 id="ai-modules">5. 🤖 AI & Data Science Modules</h2>
<p>The application is guarded by two active Machine Learning models:</p>

<ul>
  <li>
    <strong>Sentiment & Abusiveness Analysis:</strong>
    <br>
    <em>Model:</em> Fine-tuned BERT / Logistic Regression.
    <br>
    <em>Function:</em> Analyzes incoming messages to detect abusive content or distress. Implemented in `Backend/ML Models/content_moderation.py`.
  </li>
  <br>
  <li>
    <strong>NSFW Content Detection:</strong>
    <br>
    <em>Model:</em> Image Classification Transformer.
    <br>
    <em>Function:</em> Automatically scans shared images for inappropriate content before they are broadcasted to the chat.
  </li>
</ul>

<h2 id="screenshots">6. 📸 UI Screenshots</h2>

<table width="100%">
  <tr>
    <td width="50%">
      <h4 align="center">Teacher Command Center</h4>
      <img src="Preview/dashboard.jpg" alt="Teacher Dashboard" width="100%" />
    </td>
    <td width="50%">
      <h4 align="center">Friends Management</h4>
      <img src="Preview/friends.jpg" alt="Friends Management" width="100%" />
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h4 align="center">Real-Time Chat Interface</h4>
      <img src="Preview/chat.jpg" alt="Chat Window" width="100%" />
    </td>
    <td width="50%">
      <h4 align="center">Login & Authentication</h4>
      <img src="Preview/login.jpg" alt="Login Page" width="100%" />
    </td>
  </tr>
</table>

<h2 id="tech-stack">7. 🛠️ Tech Stack</h2>

<p>
  <img src="https://img.shields.io/badge/Language-Python_3.10+-yellow?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/Frontend-TailwindCSS_%2F_JS-orange?style=flat-square&logo=tailwindcss" />
  <img src="https://img.shields.io/badge/Framework-Flask-green?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL-blue?style=flat-square&logo=postgresql" />
  <img src="https://img.shields.io/badge/Realtime-Socket.IO-black?style=flat-square&logo=socket.io" />
  <img src="https://img.shields.io/badge/AI-PyTorch_%2F_Transformers-orange?style=flat-square&logo=pytorch" />
  <img src="https://img.shields.io/badge/Reports-ReportLab-red?style=flat-square&logo=adobeacrobatreader" />
</p>

<h2 id="installation">8. ⚙️ Installation & Setup</h2>

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

<h2 id="usage">9. 📖 Usage Guide</h2>
<ol>
  <li><strong>Registration:</strong> Use your <code>@uet.edu.pk</code> email to register. Select your role (Student/Faculty).</li>
  <li><strong>Faculty Dashboard:</strong> Teachers can access <code>dashboard_teachers.html</code> to create classes and view analytics.</li>
  <li><strong>Classes & Assignments:</strong>
    <ul>
        <li><strong>Faculty:</strong> Create a class, add assignments, and grade submissions.</li>
        <li><strong>Students:</strong> Join classes, view assignments, and upload solutions.</li>
    </ul>
  </li>
  <li><strong>Chat:</strong> Use the secure chat interface for peer-to-peer or group communication.</li>
  <li><strong>Admin:</strong> Log in with admin credentials to view the Sentiment Analysis heatmaps.</li>
</ol>

<h2 id="team">10. 👥 Development Team</h2>

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
      <td>Lead Developer / Full Stack Architecture</td>
      <td><a href="https://github.com/muneeb-shafique/">@muneeb</a></td>
    </tr>
    <tr>
      <td><strong>Huzaifa</strong></td>
      <td>2024-DS-47</td>
      <td>Network Security Engineer</td>
      <td><a href="#">@huzaifa</a></td>
    </tr>
    <tr>
      <td><strong>Dayan</strong></td>
      <td>2024-DS-24</td>
      <td>ML & AI Specialist</td>
      <td><a href="#">@dayan</a></td>
    </tr>
  </tbody>
</table>

<br>

<div align="center">
  <p>
    Dated: 12/30/25 | Institute of Data Science, UET
  </p>
  <img src="https://img.shields.io/badge/Status-Active_Development-brightgreen" />
  <img src="https://img.shields.io/badge/License-MIT-blue" />
</div>
