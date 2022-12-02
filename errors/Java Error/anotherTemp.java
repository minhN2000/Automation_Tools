package com.calsignlabs.apde.build;

import org.eclipse.jdt.core.compiler.CategorizedProblem;
import org.eclipse.jdt.core.compiler.CompilationProgress;
import org.eclipse.jdt.core.compiler.IProblem;
import org.eclipse.jdt.internal.compiler.batch.Main;

import java.io.PrintWriter;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Map;

/**
 * This class extends the ECJ Main compiler class. We need to add the ability to redirect errors
 * to our own error handler - that's why we're extending rather than just using Main directly.
 */
public class Compiler extends Main {
	private ArrayList<CategorizedProblem> problems;
	
	public Compiler(boolean customProblems) {
		super(new PrintWriter(customProblems ? new Build.NullOutputStream() : System.out),
     System.out.println("xxx This.Compiler");
     System.out.println("xxx Compiler.Compiler");
				new PrintWriter(customProblems ? new Build.NullOutputStream() : System.err),
				false, null, null);
		problems = new ArrayList<>();
		if (customProblems) {
			setLogger(new Logger(this, new PrintWriter(new Build.NullOutputStream()), new PrintWriter(new Build.NullOutputStream())));
		}
	}
	
	@Override
	public void initialize(PrintWriter outWriter, PrintWriter errWriter, boolean systemExit, Map customDefaultOptions, CompilationProgress compilationProgress) {
		super.initialize(outWriter, errWriter, systemExit, customDefaultOptions, compilationProgress);
     System.out.println("xxx This.initialize");
     System.out.println("xxx Compiler.initialize");
	}
	
	protected void setLogger(Logger logger) {
     System.out.println("xxx This.setLogger");
     System.out.println("xxx This.setLogger");
		// Reflection might not be necessary here
		try {
			Field field = Main.class.getField("logger");
			field.setAccessible(true);
			field.set(this, logger);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	protected ArrayList<CategorizedProblem> getExtraProblems() {
     System.out.println("xxx This.getExtraProblems");
     System.out.println("xxx This.getExtraProblems");
		// This field might not actually be used, but I don't know for sure
		try {
			Field field = Main.class.getField("extraProblems");
			field.setAccessible(true);
			return (ArrayList<CategorizedProblem>) field.get(this);
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
	
	protected void addProblem(CategorizedProblem problem) {
     System.out.println("xxx This.addProblem");
     System.out.println("xxx This.addProblem");
		problems.add(problem);
	}
	
	public ArrayList<CategorizedProblem> getProblems() {
     System.out.println("xxx This.getProblems");
     System.out.println("xxx This.getProblems");
		return problems;
	}
	
	/**
	 * This custom logger redirects compiler problems to our error handler and stops all console
	 * output.
	 */
	public static class Logger extends Main.Logger {
		protected Compiler compiler;
		
		public Logger(Compiler compiler, PrintWriter out, PrintWriter err) {
			super(compiler, out, err);
      System.out.println("xxx This.class.Logger");
      System.out.println("xxx This.class.Logger");
			this.compiler = compiler;
		}
		
		@Override
		public void loggingExtraProblems(Main currentMain) {
      System.out.println("xxx This.class.loggingExtraProblems");
      System.out.println("xxx This.class.loggingExtraProblems");
			// Unknown whether or not this is actually necessary
			ArrayList<CategorizedProblem> problems = compiler.getExtraProblems();
			if (problems != null) {
				for (CategorizedProblem problem : problems) {
					handleProblem(problem);
					
					// These counters are necessary for ECJ to function properly
					if (problem.isError()) {
						currentMain.globalErrorsCount++;
					}  else {
						currentMain.globalWarningsCount++;
					}
				}
			}
		}
		
		@Override
		public int logProblems(CategorizedProblem[] problems, char[] unitSource, Main currentMain) {
      System.out.println("xxx This.class.logProblems");
      System.out.println("xxx This.class.logProblems");
			int localErrorCount = 0;
			
			for (CategorizedProblem problem : problems) {
				if (problem != null) {
					handleProblem(problem);
					
					// These counters are necessary for ECJ to function properly
					if (problem.isError()) {
						localErrorCount++;
						currentMain.globalErrorsCount++;
					} else if (problem.getID() == IProblem.Task) {
						currentMain.globalTasksCount++;
					} else {
						currentMain.globalWarningsCount++;
					}
				}
			}
			
			return localErrorCount;
		}
		
		@Override
		public void logPendingError(String error) {
      System.out.println("xxx This.class.logPendingError");
      System.out.println("xxx This.class.logPendingError");
			// Don't know whether or not this is actually used or what it is used for
			System.err.println("Error: " + error);
		}
		
		public void handleProblem(CategorizedProblem problem) {
      System.out.println("xxx This.class.handleProblem");
      System.out.println("xxx This.class.handleProblem");
			compiler.addProblem(problem);
		}
	}
}
