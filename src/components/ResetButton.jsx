import '../styles/ResetButton.css';
export default function ResetButton({ studentId, students, setStudents }) {
  const handleReset = () => {
    const updatedStudents = students.map((student) =>
      student.id === studentId ? { ...student, usage: 0 } : student
    );
    setStudents(updatedStudents);
    alert(`Reset usage for ${studentId}`);
  };

  return <button className="reset-button" onClick={handleReset}>Reset</button>;
}