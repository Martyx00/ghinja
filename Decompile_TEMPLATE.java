/* ###
 * IP: GHIDRA
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
//Decompile an entire program

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import ghidra.app.plugin.core.script.Ingredient;
import ghidra.app.plugin.core.script.IngredientDescription;
import ghidra.app.script.GatherParamPanel;
import ghidra.app.script.GhidraScript;
import ghidra.app.util.Option;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.Address;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.decompiler.DecompiledFunction;
import ghidra.app.util.headless.HeadlessScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Listing;
import java.util.ArrayList;
import java.io.FileWriter;

public class Decompile extends HeadlessScript {

	@Override
	public void run() throws Exception {
	  	
		setHeadlessContinuationOption(HeadlessContinuationOption.ABORT);
		DecompInterface decompiler = new DecompInterface();
		
		Listing listing = currentProgram.getListing();
		FunctionIterator iter = listing.getFunctions(true);
		Function function = iter.next();
		decompiler.openProgram(function.getProgram());
		while (iter.hasNext() && !monitor.isCancelled()) {
			if (function.isExternal()) {
				function = iter.next();
				continue;
			}
			Address entryPoint = function.getEntryPoint();
			if (entryPoint != null) {
				DecompileResults decompilerResult = decompiler.decompileFunction(function, 5, null);
				DecompiledFunction decompiledFunction = decompilerResult.getDecompiledFunction();
				if (decompiledFunction == null) {
					function = iter.next();
					continue;
				}
				FileWriter myWriter = new FileWriter("PLACEHOLDER_OUTPUT"+String.valueOf(entryPoint.getOffset()));
				myWriter.write(decompiledFunction.getC());
				myWriter.close();
			}
			function = iter.next();
		}	
	}
}


