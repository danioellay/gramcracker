/*
 * Nonogram Solver in Copris
 * by Naoyuki Tamura
 * http://bach.istc.kobe-u.ac.jp/copris/puzzles/nonogram/
 */
package nonogram
import jp.kobe_u.copris._
import jp.kobe_u.copris.dsl._
import scala.io.Source

object Solver {
  var m = 0
  var n = 0
  var rows: Seq[Seq[Int]] = Seq.empty
  var cols: Seq[Seq[Int]] = Seq.empty
  def parse(source: Source) = {
    val lines = source.getLines.map(_.trim)
    m = lines.next.toInt
    n = lines.next.toInt
    rows = for (i <- 0 until m; s = lines.next)
	   yield if (s == "") Seq.empty
		 else s.split("\\s+").toSeq.map(_.toInt)
    lines.next
    cols = for (j <- 0 until n; s = lines.next)
	   yield if (s == "") Seq.empty
		 else s.split("\\s+").toSeq.map(_.toInt)
    source.close
  }
  def define = {
    for (i <- 0 until m; j <- 0 until n)
      int('x(i,j), 0, 1)
    for (i <- 0 until m; k <- 0 until rows(i).size)
      int('r(i,k), 0, n-rows(i)(k))
    for (i <- 0 until m; k <- 0 until rows(i).size-1)
      add('r(i,k) + rows(i)(k) < 'r(i,k+1))
    for (j <- 0 until n; k <- 0 until cols(j).size)
      int('c(j,k), 0, m-cols(j)(k))
    for (j <- 0 until n; k <- 0 until cols(j).size-1)
      add('c(j,k) + cols(j)(k) < 'c(j,k+1))
    for (i <- 0 until m; j <- 0 until n) {
      val rs = for (k <- 0 until rows(i).size)
	       yield 'r(i,k) <= j && 'r(i,k) + rows(i)(k) > j
      add('x(i,j) > 0 <==> Or(rs))
      val cs = for (k <- 0 until cols(j).size)
	       yield 'c(j,k) <= i && 'c(j,k) + cols(j)(k) > i
      add('x(i,j) > 0 <==> Or(cs))
    }
  }
  def showSolution = {
    for (i <- 0 until m) {
      val xs = for (j <- 0 until n)
	       yield if (solution('x(i,j)) == 0) "." else "#"
      println(xs.mkString)
    }
  }
  def main(args: Array[String]) = {
    val name = "nonogram.Solver"
    var help = false
    var quiet = false
    def parseOptions(args: List[String]): List[String] = args match {
      case "-h" :: rest =>
	{ help = true; parseOptions(rest) }
      case "-s1" :: solver :: rest =>
	{ use(new sugar.Solver(csp, new sugar.SatSolver1(solver))); parseOptions(rest) }
      case "-s2" :: solver :: rest =>
	{ use(new sugar.Solver(csp, new sugar.SatSolver2(solver))); parseOptions(rest) }
      case "-smt" :: solver :: rest =>
	{ use(new smt.Solver(csp, new smt.SmtSolver(solver))); parseOptions(rest) }
      case "-q" :: rest =>
	{ quiet = true; parseOptions(rest) }
      case _ =>
	args
    }
    parseOptions(args.toList) match {
      case Nil if ! help =>
	parse(Source.stdin)
      case file :: Nil if ! help =>
	parse(Source.fromFile(file))
      case _ => {
        println("Usage: scala " + name + " [options] [inputFile]")
	println("\t-h          : Help")
	println("\t-q          : Quiet output")
	println("\t-s1 solver  : Use SAT solver (minisat, etc.)")
	println("\t-s2 solver  : Use SAT solver (precosat, etc.)")
	println("\t-smt solver : Use SMT solver (z3, etc.)")
	System.exit(1)
      }
    }
    define
    if (find) {
      if (! quiet)
	showSolution
      if (findNext)
	println("Multiple solutions")
      else
	println("Unique solution")
    }
  }
}
