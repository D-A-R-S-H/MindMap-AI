export default function ErrorMessage({ message }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      Something went wrong: {message}. Please refresh and try again.
    </div>
  );
}