name := "copris-nonogram"
version := "1.2"

scalaVersion := "2.10.3"

unmanagedBase := baseDirectory.value / "lib"

// Define main class for both package and assembly tasks
mainClass in (Compile, packageBin) := Some("nonogram.Solver")
mainClass in assembly := Some("nonogram.Solver")

libraryDependencies ++= Seq(
  "org.scala-lang" % "scala-library" % scalaVersion.value,
  "org.scala-lang" % "scala-compiler" % scalaVersion.value,
  "org.scala-lang" % "scala-reflect" % scalaVersion.value
)

// Assembly settings
assemblyMergeStrategy in assembly := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}
