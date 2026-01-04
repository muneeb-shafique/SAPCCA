import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from models import User, Assignment, AssignmentSubmission, db

# --- DSA Implementation ---
def merge_sort_students(students_scores):
    """
    Sorts a list of (student_name, total_score) tuples using Merge Sort.
    Time Complexity: O(N log N)
    """
    if len(students_scores) <= 1:
        return students_scores

    mid = len(students_scores) // 2
    left = merge_sort_students(students_scores[:mid])
    right = merge_sort_students(students_scores[mid:])

    return merge(left, right)

def merge(left, right):
    sorted_list = []
    i = j = 0
    while i < len(left) and j < len(right):
        # Sort descending (higher score first)
        if left[i][1] >= right[j][1]:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list

# --- Graph Generation ---
def generate_performance_graphs(teacher_id=None, class_id=None):
    graphs = {}

    # 1. Fetch Data
    query_assign = Assignment.query
    query_subs = AssignmentSubmission.query

    if teacher_id:
        query_assign = query_assign.filter_by(created_by=teacher_id)
        # Submissions for assignments created by this teacher
        # This is a bit complex in pure ORM without joins, so we filter in memory or fetch IDs
        assign_ids = [a.id for a in query_assign.all()]
        if not assign_ids:
             return {}
        query_subs = query_subs.filter(AssignmentSubmission.assignment_id.in_(assign_ids))

    elif class_id:
        query_assign = query_assign.filter_by(class_id=class_id)
        assign_ids = [a.id for a in query_assign.all()]
        if not assign_ids:
             return {}
        query_subs = query_subs.filter(AssignmentSubmission.assignment_id.in_(assign_ids))
    
    assignments = query_assign.all()
    submissions = query_subs.all()
    # Users (students) involved in these submissions need to be fetched
    student_ids = set(s.student_id for s in submissions)
    users = User.query.filter(User.id.in_(student_ids)).all()

    if not assignments or not submissions:
        return {}

    # Convert to DataFrame for easier processing (except where DSA is processed manually)
    df_subs = pd.DataFrame([{
        'student_id': s.student_id,
        'assignment_id': s.assignment_id,
        'grade': s.grade if s.grade is not None else 0
    } for s in submissions])

    df_assigns = pd.DataFrame([{
        'id': a.id,
        'title': a.title
    } for a in assignments])
    
    user_map = {u.id: u.display_name or u.email for u in users}

    # --- Graph 1: Average Score per Assignment ---
    if not df_subs.empty:
        avg_scores = df_subs.groupby('assignment_id')['grade'].mean().reset_index()
        avg_scores = avg_scores.merge(df_assigns, left_on='assignment_id', right_on='id')
        
        plt.figure(figsize=(10, 6))
        plt.bar(avg_scores['title'], avg_scores['grade'], color='skyblue')
        plt.title('Average Score per Assignment')
        plt.xlabel('Assignment')
        plt.ylabel('Average Grade')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        graphs['avg_assignment_score'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

    # --- Graph 2: Student Rankings (Using DSA Merge Sort) ---
    student_totals = df_subs.groupby('student_id')['grade'].sum().reset_index()
    student_list = []
    for _, row in student_totals.iterrows():
        name = user_map.get(row['student_id'], f"User {row['student_id']}")
        student_list.append((name, row['grade']))

    # Apply DSA: Merge Sort
    sorted_students = merge_sort_students(student_list)
    top_5 = sorted_students[:5]

    if top_5:
        names, scores = zip(*top_5)
        plt.figure(figsize=(10, 6))
        plt.barh(names, scores, color='lightgreen')
        plt.title('Top 5 Performing Students')
        plt.xlabel('Total Score')
        plt.gca().invert_yaxis() # Highest at top
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        graphs['top_students'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

    return graphs
