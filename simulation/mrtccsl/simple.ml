open Mrtccsl
open Prelude
open Analysis.FunctionalChain
module FnCh = Analysis.FunctionalChain.Make (String) (Number.Rational)
module A = FnCh.A
module S = FnCh.S
open Number.Rational
open FnCh
open Halsoa
open Definition
module N = Number.Rational

type 'n aebsimple_config =
  { name : string
  ; n_sigma : int
  ; absolute : bool
  ; sensor_sampling_period : 'n * 'n
  ; sensor_latency : 'n * 'n
  ; sensor_offset : 'n
  ; controller_exec_time : 'n * 'n
  ; actuator_sampling_period : 'n * 'n
  ; actuator_latency : 'n * 'n
  ; actuator_offset : 'n
  ; relaxed_sched : bool
  ; delayed_comm : ('n * 'n) option
  ; cores : int option
  }
[@@deriving map]

let sigma n (l, r) =
  let dev = (r - l) / of_int (Int.mul 2 n) in
  let mean = l + ((r - l) / of_int 2) in
  (* Printf.printf "mean: %s dev:%s\n" (N.to_string mean) (N.to_string dev); *)
  Automata.Simple.Normal { mean; dev }
;;

let range_to_bound_dist ~n_sigma bounds = { bounds; dist = sigma n_sigma bounds }

let make_periodic_policy ~absolute ~n_sigma range offset =
  if absolute
  then (
    let l, r = range in
    let jitter = (r - l) / of_int 2 in
    let period = l + jitter in
    `AbsoluteTimer (period, range_to_bound_dist ~n_sigma (N.neg jitter, jitter), offset))
  else `CumulativeTimer (range_to_bound_dist ~n_sigma range, offset)
;;

let aebsimple_template
      { n_sigma
      ; absolute
      ; sensor_sampling_period
      ; sensor_latency
      ; sensor_offset
      ; controller_exec_time
      ; actuator_sampling_period
      ; actuator_latency
      ; actuator_offset
      ; _
      }
  : _ system
  =
  let components =
    [ { services =
          [ { name = "aeb.control"
            ; inputs = [ "radar" ]
            ; outputs = [ "brake" ]
            ; execution_time = range_to_bound_dist ~n_sigma controller_exec_time
            ; policy = `Signal "radar"
            }
          ]
      }
    ]
  and hal =
    [ ( "radar"
      , Sensor
          { as_device = true
          ; policy =
              make_periodic_policy ~absolute ~n_sigma sensor_sampling_period sensor_offset
          ; latency = range_to_bound_dist ~n_sigma sensor_latency
          } )
    ; ( "brake"
      , Actuator
          { policy =
              make_periodic_policy
                ~absolute
                ~n_sigma
                actuator_sampling_period
                actuator_offset
          ; latency = range_to_bound_dist ~n_sigma actuator_latency
          } )
    ]
    |> List.to_seq
    |> Hashtbl.of_seq
  in
  components, hal
;;

let useless_def_spec chain =
  let open Mrtccsl.Analysis.FunctionalChain in
  let open Mrtccsl.Rtccsl in
  let constraints, _ =
    List.fold_left
      (fun (spec, prev) -> function
         | `Sampling, c ->
           let useful = Printf.sprintf "%s++" c
           and useless = Printf.sprintf "%s--" c in
           ( List.append
               [ Sample { out = useful; arg = prev; base = c }
               ; Minus { out = useless; arg = c; except = [ useful ] }
               ]
               spec
           , c )
         | `Causality, c -> spec, c)
      ([], chain.first)
      chain.rest
  in
  Mrtccsl.Rtccsl.constraints_only constraints
;;

let of_sys ?cores ?delayed_comm ~n_sigma ~relaxed_sched sys chain =
  let dist, spec =
    Semantics.of_system
      ~relaxed_sched
      ?delayed_comm:(Option.map (range_to_bound_dist ~n_sigma) delayed_comm)
      ?cores
      sys
  in
  let tasks = Semantics.system_tasks sys in
  dist, Mrtccsl.Rtccsl.merge spec (useless_def_spec chain), tasks
;;

let of_aebsimple_config c =
  let c = map_aebsimple_config of_int c in
  let { name; n_sigma; relaxed_sched; delayed_comm; cores; _ } = c in
  let sys = aebsimple_template c in
  let chain = Semantics.signals_to_chain sys [ "radar"; "brake" ] in
  let dist, spec, tasks = of_sys ?cores ~n_sigma ?delayed_comm ~relaxed_sched sys chain in
  name, dist, spec, tasks, chain
;;

let aebsimple_variants absolute =
  [ { name = "c1"
    ; n_sigma = 2
    ; absolute
    ; sensor_sampling_period = 14, 16
    ; sensor_latency = 1, 3
    ; sensor_offset = 0
    ; controller_exec_time = 2, 8
    ; actuator_sampling_period = 14, 16
    ; actuator_latency = 1, 3
    ; actuator_offset = 0
    ; relaxed_sched = false
    ; delayed_comm = None
    ; cores = None
    }
  ; { name = "c2"
    ; n_sigma = 2
    ; absolute
    ; sensor_sampling_period = 14, 16
    ; sensor_latency = 1, 3
    ; sensor_offset = 0
    ; controller_exec_time = 2, 8
    ; actuator_sampling_period = 4, 6
    ; actuator_latency = 1, 3
    ; actuator_offset = 0
    ; relaxed_sched = false
    ; delayed_comm = None
    ; cores = None
    }
  ; { name = "c3"
    ; n_sigma = 2
    ; absolute
    ; sensor_sampling_period = 14, 16
    ; sensor_latency = 1, 3
    ; sensor_offset = 0
    ; controller_exec_time = 2, 4
    ; actuator_sampling_period = 14, 16
    ; actuator_latency = 1, 3
    ; actuator_offset = 0
    ; relaxed_sched = false
    ; delayed_comm = None
    ; cores = None
    }
  ; { name = "c4"
    ; n_sigma = 2
    ; absolute
    ; sensor_sampling_period = 14, 16
    ; sensor_latency = 1, 3
    ; sensor_offset = 0
    ; controller_exec_time = 2, 4
    ; actuator_sampling_period = 4, 6
    ; actuator_latency = 1, 3
    ; actuator_offset = 0
    ; relaxed_sched = false
    ; delayed_comm = None
    ; cores = None
    }
  ]
  |> List.map of_aebsimple_config
;;

let step = of_int 1 / of_int 1000

let random_strat =
  ST.Solution.avoid_empty
  @@ ST.Solution.random_label
       (ST.Num.random_leap
          ~upper_bound:(of_int 1000)
          ~ceil:(round_up step)
          ~floor:(round_down step)
          ~rand:random)
;;

let rec create_dir fn =
  if not (Sys.file_exists fn)
  then (
    let parent_dir = Filename.dirname fn in
    create_dir parent_dir;
    Sys.mkdir fn 0o755)
;;

let generate_trace
      ~print_svgbob
      ~print_trace
      ~steps
      ~horizon
      directory
      dist
      system_spec
      tasks
      func_chain_spec
      i
  =
  let _ = Random.init 2174367364 in
  let strategy = ST.Solution.refuse_empty random_strat in
  let basename = Printf.sprintf "%s/%i" directory i in
  let sem = Earliest
  and points_of_interest = points_of_interest func_chain_spec in
  let session, trace, _, chains, _ =
    FnCh.functional_chains
      ~sem
      (strategy, steps, horizon)
      dist
      system_spec
      func_chain_spec
  in
  if print_svgbob
  then (
    let clocks = List.sort_uniq String.compare (Rtccsl.spec_clocks system_spec) in
    let trace_file = open_out (Printf.sprintf "./%s.svgbob" basename) in
    Export.trace_to_vertical_svgbob
      ~numbers:false
      ~tasks
      session
      clocks
      (Format.formatter_of_out_channel trace_file)
      trace;
    close_out trace_file);
  if print_trace
  then (
    let trace_file = open_out (Printf.sprintf "%s.trace" basename) in
    Export.trace_to_csl session (Format.formatter_of_out_channel trace_file) trace;
    close_out trace_file);
  let reactions =
    FnCh.reaction_times session points_of_interest (Iter.of_dynarray chains)
  in
  reactions
;;

module Opt = Mrtccsl.Optimization.Order.Make (String)

let process_config
      ~print_svgbob
      ~print_trace
      ~directory
      ~processor
      ~horizon
      ~steps
      (name, dist, spec, tasks, chain)
  =
  (let open Rtccsl in
   let len = List.length spec.constraints in
   let spec = Opt.optimize spec in
   assert (len = List.length spec.constraints));
  let prefix = Filename.concat directory name in
  let _ = print_endline prefix in
  let _ = create_dir prefix in
  let _ =
    print_endline
      (Rtccsl.show_specification
         Format.pp_print_string
         Format.pp_print_string
         Format.pp_print_string
         (fun state v ->
            let s = to_string v in
            Format.pp_print_string state s)
         spec)
  in
  let reaction_times =
    processor
    @@ generate_trace
         ~print_svgbob
         ~print_trace
         ~steps
         ~horizon
         prefix
         dist
         spec
         tasks
         chain
  in
  let points_of_interest = points_of_interest chain in
  let categories = categorization_points chain in
  let data_file = open_out (Printf.sprintf "%s/reaction_times.csv" prefix) in
  let _ =
    FnCh.reaction_times_to_csv categories points_of_interest data_file reaction_times
  in
  close_out data_file
;;

let () =
  let usage_msg =
    "simple [-t <traces>] [-n <cores>] [-h <trace horizon>] [-bob] [-cadp] <dir>"
  in
  let traces = ref 1
  and cores = ref 1
  and steps = ref 1000
  and horizon = ref 10_000.0
  and print_svgbob = ref false
  and print_trace = ref false in
  let speclist =
    [ "-t", Arg.Set_int traces, "Number of traces to generate"
    ; "-c", Arg.Set_int cores, "Number of cores to use"
    ; "-h", Arg.Set_float horizon, "Max time of simulation"
    ; "-s", Arg.Set_int steps, "Max steps of simulation"
    ; "-bob", Arg.Set print_svgbob, "Print svgbob trace"
    ; "-cadp", Arg.Set print_trace, "Print CADP trace"
    ]
  in
  let directory = ref None in
  let _ = Arg.parse speclist (fun dir -> directory := Some dir) usage_msg in
  let recommended_cores = Stdlib.Domain.recommended_domain_count () in
  if !traces < 1 then invalid_arg "number of traces should be positive";
  if !cores < 1 then invalid_arg "number of cores should be positive";
  if !steps < 1 then invalid_arg "number of steps should be positive";
  if !horizon <= 0.0 then invalid_arg "horizon should be positive";
  let processor =
    if !cores <> 1
    then (
      let pool =
        Domainslib.Task.setup_pool ~num_domains:(Int.min !cores recommended_cores) ()
      in
      fun f ->
        Domainslib.Task.run pool (fun _ ->
          Domainslib.Task.parallel_for_reduce
            ~chunk_size:1
            ~start:0
            ~finish:(Int.pred !traces)
            ~body:f
            pool
            Iter.append
            Iter.empty))
    else
      fun f ->
        Iter.int_range ~start:0 ~stop:(Int.pred !traces)
        |> Iter.map f
        |> Iter.fold Iter.append Iter.empty
  in
  let directory = Option.get !directory in
  List.iter
    (process_config
       ~processor
       ~print_svgbob:!print_svgbob
       ~print_trace:!print_trace
       ~directory:(Filename.concat directory "absolute")
       ~steps:!steps
       ~horizon:(of_float !horizon))
    (aebsimple_variants true);
  List.iter
    (process_config
       ~processor
       ~print_svgbob:!print_svgbob
       ~print_trace:!print_trace
       ~directory:(Filename.concat directory "cumulative")
       ~steps:!steps
       ~horizon:(of_float !horizon))
    (aebsimple_variants false)
;;
