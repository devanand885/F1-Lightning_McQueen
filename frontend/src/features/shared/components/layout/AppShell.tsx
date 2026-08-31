import Navbar from "./Navbar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Navbar />

      <main
        style={{
          minHeight: "100vh",
        }}
        className="p-4 bg-bg-base"
      >
        {children}
      </main>
    </>
  );
}
